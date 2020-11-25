#!/usr/bin/python3

import sys, os, textwrap

from dns_add_record import create_db_record, serial_now, touch_db_serial
from dns_util import as_file, reload_name_server


BASE_ZONE = "pieter-fiers.sb.uclllabs.be"
ZONE_DB_PATH_PREFIX = "/etc/bind/mrt-zones"
ZONE_CONFIG_PATH = "/etc/bind/named.conf.local.mrt"
PARENT_GLUE_DB_PATH = "/etc/bind/mrt-zones/parent-glue"
NAMESERVER = "ns.pieter-fiers.sb.uclllabs.be."
DEFAULT_TTL = '5m'

def to_zone_db_path(subzone: str):
    filename = f"db.{subzone}.pieter-fiers.sb.uclllabs.be"
    return os.path.join(ZONE_DB_PATH_PREFIX, filename) 

def add_parent_glue_records(subzone: str):
    create_db_record(PARENT_GLUE_DB_PATH, subzone, "NS", NAMESERVER)
    touch_db_serial("/etc/bind/zones/db.pieter-fiers.sb.uclllabs.be")

def initialize_zone_db(file_or_path: str):
    with as_file(file_or_path, 'w+') as f:
        f.write(f"$TTL {DEFAULT_TTL}\n")
        ns = "ns.pieter-fiers.sb.uclllabs.be."
        admin_mail = "admin.pieter-fiers.sb.uclllabs.be."
        soa_data = f"{ns} {admin_mail} ({serial_now()} 604800 86400 2419200 604800)"
        create_db_record(f, "@", "SOA", soa_data)
        create_db_record(f, None, "NS", NAMESERVER)

def create_zone_config(subzone: str, db_path: str):
    with open(ZONE_CONFIG_PATH, 'a') as f:
        full_zone = f"{subzone}.{BASE_ZONE}"
        config = textwrap.dedent(f"""\
            zone "{full_zone}" {{
                type master;
                file "{db_path}";
            }};
        """)
        f.write(config)

def create_zone_db(subzone: str):
    db_path = to_zone_db_path(subzone)
    initialize_zone_db(db_path)
    add_parent_glue_records(subzone)
    create_zone_config(subzone, db_path)

def main():
    args = sys.argv

    # root detection not necessary, just fail at creating db file
    # if not os.geteuid() == 0:
    #     sys.exit(f"{args[0]} needs to be executed as root")

    if len(args) != 2:
        sys.exit(f"usage: {args[0]} ZONE_NAME")

    subzone = args[1]
    create_zone_db(subzone)

    reload_name_server()


if __name__ == "__main__":
    main()

