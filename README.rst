=========================
Docker PostgreSQL Backup
=========================

Docker image that runs a cron job which dumps a Postgres database, and uploads it to an Amazon S3 bucket.

Required environment variables
==============================

* :code:`CRON_SCHEDULE`: The time schedule part of a crontab file (e.g: :code:`15 3 * * *` for every night 03:15)
* :code:`DB_HOST`: Postgres hostname
* :code:`DB_PORT`: Postgres port
* :code:`DB_PASS`: Postgres password
* :code:`DB_USER`: Postgres username
* :code:`DB_NAMES`: Names of database "db1 db2"
* :code:`DB_SSLMODE`: Sslmode of database
* :code:`S3_PATH`: Amazon S3 path in the format: s3://bucket-name/some/path
* :code:`KEEP_BACKUP_DAYS_IN_AWS`: How long store backup in aws (default 30 days)
* :code:`AWS_ACCESS_KEY_ID`
* :code:`AWS_SECRET_ACCESS_KEY`
* :code:`AWS_DEFAULT_REGION`
* :code:`BACKUP_FILENAME_PREFIX`
* :code:`PG_DUMP_MANUAL_FEATURES--exclude-table-data 'table_name'

Optional environment variables
==============================

* :code:`WEBHOOK`: If specified, an HTTP request will be sent to this URL
* :code:`WEBHOOK_METHOD`: By default the webhook's HTTP method is GET, but can be changed using this variable
* :code:`KEEP_BACKUP_DAYS`: The number of days to keep backups for when pruning old backups

Restoring a backup
==================

This image can also be run as a one off task to restore one of the backups. 
To do this, we run the container with the command: :code:`/backup/restore.sh [S3-filename]`.

The following environment variables are required:

* :code:`DB_HOST`: Postgres hostname
* :code:`DB_PASS`: Postgres password
* :code:`DB_USER`: Postgres username
* :code:`DB_NAME`: Name of database
* :code:`S3_PATH`: Amazon S3 path in the format: s3://bucket-name/some/path
* :code:`AWS_ACCESS_KEY_ID`
* :code:`AWS_SECRET_ACCESS_KEY`
* :code:`AWS_DEFAULT_REGION`

