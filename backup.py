import pathlib
import datetime
import gzip
import subprocess
import os

mysqldump_path = os.environ.get("MYSQLDUMP_PATH") if os.environ.get("MYSQLDUMP_PATH") else "/usr/bin/mysqldump"

backup_prefix = pathlib.Path(os.environ["ODIR"])
backup_dbs = os.environ["DBS"].split(",")


def backup(backup_db):
    firstbackup = False
    backup_file = pathlib.Path(backup_prefix / backup_db / (backup_db + ".sql"))

    if backup_file.exists():
        # Compress the latest backup. It becomes the penultimate backup. If this is the first time backing up, skip.
        with open(backup_file, 'rb') as latest_backup:
            backup_crdate = datetime.datetime.fromtimestamp(backup_file.stat().st_ctime).strftime("_%Y_%m_%d_%H_%M_%S")
            backup_ofile = pathlib.Path(backup_prefix) / backup_db / f"{backup_file.stem}{backup_crdate}.sql.gz"

            print(backup_ofile)
            with gzip.open(backup_ofile, 'w') as compressed_penultimate_backup:
                compressed_penultimate_backup.write(latest_backup.read())


    # Back up mysql database to SQL files.
    backup_file.parent.mkdir(exist_ok=True)
    with open(backup_file, 'wb') as latest_backup:
        backup_command = subprocess.check_output(f"{mysqldump_path} {backup_db}", shell=True)
        latest_backup.write(backup_command)

for backup_db in backup_dbs:
    backup(backup_db)
