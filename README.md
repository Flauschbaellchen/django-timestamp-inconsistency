# Proof of concept for the timestamp inconsistency

## Preparations

1. Set up PostgreSQL with pgpool - single instance servers are not affected.
   For this POC, the Bitnami Helm chart [bitnami/postgresql-ha](https://github.com/bitnami/charts/tree/main/bitnami/postgresql-ha) has been used.
   The following values had been provided:
   ```yaml
   volumePermissions:
     enabled: true
   postgresql:
     extendedConf: |-
       log_lock_waits = on
       log_statement = 'all'
       log_timezone = 'Europe/Berlin'
       timezone = 'Europe/Berlin'
       lc_time = 'en_US.UTF-8'
     livenessProbe:
       initialDelaySeconds: 90
   ```

2. Install environment:
   ```
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -r requirements.txt
   ```

## Running checks

1. Export credentials (adjust to your needs):

   ```bash
   export PGPASSWORD="xxxx"
   export PGUSER="postgres"
   export PGHOST="localhost"
   export PGDATABASE="postgres"
   ```

2. Run checks within Django environment:
   ```bash
   ./manage.py poc
   ```

   Django will run within UTC (`TIME_ZONE=UTC`) and will use TZ-aware timestamps (`USE_TZ=True`).  
   This check will break very likely within the first 5 iterations.   
   Note, that a statement `SELECT set_config('TimeZone', 'UTC', false)` will be executed.

   Running with `PGTZ=UTC` set to the environment will solve this issue.
   The select-statement `set_config` is not executed in this case. 

3. Run checks against `psql`.  
   `psql` needs to be in `$PATH`.
   ```bash
   ./poc.bash
   ```
   This check runs without any issues, independent of `PGTZ=UTC` or `PGTZ=Europe/Berlin`.

## Further notes

* Also tested against Django 4.2.7 and psycopg2-binary 2.9.9 with same results.
* Similar issue: https://code.djangoproject.com/ticket/35240
