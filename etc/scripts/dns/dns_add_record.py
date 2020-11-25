#!/usr/bin/python3

import sys, os, re, argparse, io
from datetime import datetime

from dns_util import as_file, reload_name_server


ZONE_DB_PATH_PREFIX = "/etc/bind/mrt-zones"

def serial_now():
    return int(datetime.now().strftime("%Y%m%d"))

def empty_if_none(s: str):
    return '' if s is None else s

def create_db_record(file_or_path: str, label: str, record_type: str, data: str, ttl: int = None, record_class: str = 'IN'):
    with as_file(file_or_path, 'w') as f:
        f.seek(0, io.SEEK_END)
        record_args = map(empty_if_none, [
            label, ttl, record_class, record_type, data
        ])
        recordstr = "\t".join(record_args) + '\n'
        f.write(recordstr)

SERIAL_RE = re.compile(r"SOA.*?\(.*?(\d+)", re.MULTILINE | re.DOTALL)
def touch_db_serial(file_or_path: str, serial: int = serial_now()):
    with as_file(file_or_path, 'r+') as f:
        f.seek(0)
        content = f.read()

        # Get old
        serial_matches = SERIAL_RE.search(content)
        serial_start = serial_matches.start(1)
        serial_end = serial_matches.end(1)
        serial_old = int(serial_matches.group(1))

        # Calculate new
        if serial <= serial_old:
            serial = serial_old + 1
        
        # Insert new, overwriting old
        content_new = content[:serial_start] + str(serial) + content[serial_end:]
        f.seek(0)
        f.write(content_new)

def main():
    parser = argparse.ArgumentParser(description='Add a bind9 DNS record to an existing mrt zone.')
    parser.add_argument('-t', '--type', default='A', help="record type (default: 'A')")
    parser.add_argument('subdomain', type=str, help="leftmost domain segment/label of the record's full label (ex: 'www')")
    parser.add_argument('data', type=str, help="record data (ex: 12.34.56.78)")
    parser.add_argument('zone', type=str, help="db zone name (without trailing dot, ex: 'slimme-rik.sb.uclllabs.be')", nargs='?')

    args = parser.parse_args()

    zone = None
    if args.type == 'CNAME':
        # <data> arg *is* the zone. Don't ask questions
        zone = args.data
    else:
        if args.zone is None:
            exit(f"<zone> is required for all record types except CNAME")
        zone = args.zone

    filename = f"db.{zone}"
    path = os.path.join(ZONE_DB_PATH_PREFIX, filename)
    try:
        with open(path, 'r+') as f:
            if args.type in ['SOA', 'A']:
                create_db_record(f, args.subdomain, args.type, args.data)
            elif args.type == 'CNAME':
                 create_db_record(f, args.subdomain, 'CNAME', '@')
            elif args.type == 'MX':
                create_db_record(f, None, 'MX', args.subdomain)
                create_db_record(f, args.subdomain, 'A', args.data)
            else:
                raise NotImplementedError(f"Creating records of type '{args.type}'")
            touch_db_serial(f)
    except FileNotFoundError:
        exit(f"Zone record db not found, create it using dns_add_zone")

    reload_name_server()

if __name__ == "__main__":
    main()
