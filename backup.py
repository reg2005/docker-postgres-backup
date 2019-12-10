    #!/usr/bin/python

import os
import subprocess
import sys
from datetime import datetime, timedelta

BACKUP_DIR = '/backup/backupsTmp'
S3_PATH = os.environ["S3_PATH"]
DB_NAMES = os.environ["DB_NAMES"]
DB_PASS = os.environ["DB_PASS"]
DB_USER = os.environ["DB_USER"]
DB_HOST = os.environ["DB_HOST"]
PG_DUMP_MANUAL_FEATURES = os.environ["PG_DUMP_MANUAL_FEATURES"] or ""
DB_PORT = os.environ.get("DB_PORT") or 5432
DB_SSLMODE = os.environ.get("DB_SSLMODE") or "disable"
WEBHOOK = os.environ.get("WEBHOOK")
WEBHOOK_METHOD = os.environ.get("WEBHOOK_METHOD") or "GET"
KEEP_BACKUP_DAYS = int(os.environ.get("KEEP_BACKUP_DAYS") or 30)

KEEP_BACKUP_DAYS_IN_AWS = int(os.environ.get("KEEP_BACKUP_DAYS_IN_AMAZON", 15))
DATE_BACKUP_EXPIRE_AWS = (datetime.utcnow()+timedelta(days=KEEP_BACKUP_DAYS_IN_AWS)).strftime('%Y-%m-%dT%H:%M:%SZ')
dt = datetime.now()

if not S3_PATH.endswith("/"):
    S3_PATH = S3_PATH + "/"

def cmd(command):
    try:
        subprocess.check_output([command], shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        sys.stderr.write("\n".join([
            "Command execution failed. Output:",
            "-"*80,
            e.output,
            "-"*80,
            ""
        ]))
        raise

def backup_exists():
    return os.path.exists(backup_file)

def get_backupFile(name):
    return os.path.join(BACKUP_DIR, name) + "_" + dt.strftime("%Y-%m-%d_%I:%M%p")

def take_backup(dbName):
    backup_file = get_backupFile(dbName)
    #if backup_exists():
    #    sys.stderr.write("Backup file already exists!\n")
    #    sys.exit(1)
    
    # trigger postgres-backup
    cmd("env PGPASSWORD=%s SSL=%s pg_dump -Z4 -Fc -h %s -p %s -U %s %s > %s %s" % (
        DB_PASS,
        DB_SSLMODE,
        DB_HOST,
        DB_PORT,
        DB_USER,
        dbName,
        backup_file,
        PG_DUMP_MANUAL_FEATURES
    ))

def upload_backup(dbName):
    backup_file = get_backupFile(dbName)
    cmd("tar -czvf %s %s" % (backup_file + '.tar.gz', backup_file))
    print ("Backup will expired at %s" % DATE_BACKUP_EXPIRE_AWS)
    cmd("aws s3 cp %s %s --expires %s" % (backup_file + '.tar.gz', S3_PATH, DATE_BACKUP_EXPIRE_AWS))
    cmd("rm %s" % (backup_file))

def prune_local_backup_files():
    cmd("rm -rf %s/*" % (BACKUP_DIR))

def log(msg):
    print "[%s]: %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)

def main():
    alphabet = DB_NAMES
    databases = alphabet.split() #split string into a list
    for db in databases:
        start_time = datetime.now()
        log("Dumping database")
        take_backup(db)
        log("Uploading to S3")
        upload_backup(db)
        log("Pruning local backup copies")

    prune_local_backup_files()
    
    if WEBHOOK:
        log("Making HTTP %s request to webhook: %s" % (WEBHOOK_METHOD, WEBHOOK))
        cmd("curl -X %s %s" % (WEBHOOK_METHOD, WEBHOOK))
    
    log("Backup complete, took %.2f seconds" % (datetime.now() - start_time).total_seconds())
    sys.exit(0)


if __name__ == "__main__":
    main()

