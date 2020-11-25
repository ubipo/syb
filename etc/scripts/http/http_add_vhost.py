#!env/bin/python

import os, sys, textwrap, socket, subprocess
import dns.resolver


VHOST_CONF_DIR_PATH = "/etc/nginx/sites-enabled-mrt"
DOC_ROOT_DIR_PATH = "/var/www/mrt"
LOG_DIR_PATH = "/var/log/nginx/mrt"


def create_vhost_conf(domain: str, docroot_path: str, log_dir_path: str):
    conf_path = os.path.join(VHOST_CONF_DIR_PATH, domain)
    access_log_path = os.path.join(log_dir_path, "access.log")
    error_log_path = os.path.join(log_dir_path, "error.log")
    config = textwrap.dedent(f"""\
        server {{
            server_name {domain};

            root {docroot_path};

            location / {{
                try_files /index.txt =404;
            }}

            access_log {access_log_path};
            error_log {error_log_path};
        }}""")
    with open(conf_path, 'w') as f:
        f.write(config)

def create_docroot_files(docroot_path: str, domain: str):
    index_path = os.path.join(docroot_path, "index.txt")
    with open(index_path, 'w') as f:
        f.write(f"welcome {domain}")

def create_dir_safe(path: str):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

def create_vhost(domain: str):
    log_dir_path = os.path.join(LOG_DIR_PATH, domain)
    docroot_path = os.path.join(DOC_ROOT_DIR_PATH, domain)
    create_dir_safe(log_dir_path)
    create_dir_safe(docroot_path)
    create_docroot_files(docroot_path, domain)
    create_vhost_conf(domain, docroot_path, log_dir_path)

def reload_nginx():
    cmd = ["nginx", "-s", "reload"]
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        raise Exception(f"Error running \"{' '.join(cmd)}\"; exited with non-zero error code. Try running it manually?")
    if res.stderr.strip():
        raise Exception(f"Error running \"{' '.join(cmd)}\"; exited with non-empty stderr. Try running it manually?")

resv = dns.resolver.Resolver()
resv.nameservers = ['::1']

def get_a_record(domain: str):
    answer = resv.resolve(domain, 'A')
    return next(answer.__iter__()).address

def main():
    args = sys.argv

    # root detection not necessary, just fail at creating vhost conf file
    # if not os.geteuid() == 0:
    #     sys.exit(f"{args[0]} needs to be executed as root")

    if len(args) != 2:
        sys.exit(f"usage: {args[0]} DOMAIN")

    domain = args[1]
    try:
        get_a_record(domain)
    except dns.resolver.NoNameservers:
        sys.exit(f"Cannot create vhost for non-existing domain: {domain}")
    
    create_vhost(domain)
    reload_nginx()


if __name__ == "__main__":
    main()
