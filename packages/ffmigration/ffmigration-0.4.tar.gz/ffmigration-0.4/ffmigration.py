#!/usr/bin/env python
import sys
import logging
from optparse import OptionParser
import datetime
import MySQLdb
from MySQLdb.cursors import DictCursor
from MySQLdb import OperationalError, ProgrammingError

import os

VERSION = "0.4"

TABLE_NAME = "migration_history"


log = logging.getLogger(__file__)


class DatabaseDriver(object):

    create_table_sql = """
    CREATE TABLE %s (
      id int(11) NOT NULL AUTO_INCREMENT,
      name varchar(255) COLLATE utf8_bin NOT NULL,
      applied timestamp NOT NULL
            DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      PRIMARY KEY (`id`)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
    """ % TABLE_NAME
    check_migration = "select * from %s where name=%%s" % TABLE_NAME

    insert_migration = """insert into %s (name,applied)
        values (%%s,%%s)""" % TABLE_NAME

    def __init__(self, connection, schema, noop=False):
        self.connection = connection
        self.cursor = connection.cursor()
        self.schema = schema
        self.noop = noop

    def check_table_exists(self, table):
        sql = """select TABLE_NAME from information_schema.TABLES
                where TABLE_SCHEMA=%s and TABLE_NAME=%s"""
        self.cursor.execute(sql, (self.schema, table))
        return bool(self.cursor.fetchone())

    def create_migration_table(self):
        self.execute(self.create_table_sql)

    def check_migration_table(self):

        if self.check_table_exists(TABLE_NAME):
            return

        log.info("Creating migration history table...")
        self.create_migration_table()
        log.info("done.")
        self.commit()

    def commit(self):
        self.connection.commit()

    def check_migration_applied(self, migration):
        self.cursor.execute(self.check_migration, (migration, ))
        return bool(self.cursor.fetchone())

    def set_migration_applied(self, migration):
        now = datetime.datetime.now()
        self.execute(self.insert_migration, (migration, now))

        return bool(self.cursor.fetchone())

    def execute(self, sql, args=None):
        if args:
            debug_sql = sql % args
        else:
            debug_sql = sql

        log.debug(debug_sql)
        if not self.noop:
            self.cursor.execute(sql, args)


ESCAPED_SEMICOLON = "@@ESCAPED_SEMICOLON@@"


class MigrationSQLError(Exception):
    def __init__(self, exception, msg):
        super(MigrationSQLError, self).__init__(msg)
        self.exception = exception


class MigrationRunner(object):
    def __init__(self, driver):
        self.driver = driver
        self.run_times = {}
        self.start_time = datetime.datetime.now()
        self.end_time = None

    def run_sql_script(self, migration_file):

        migration = migration_file.read()
        # escape \;
        migration = migration.replace(r'\;', ESCAPED_SEMICOLON)
        steps = migration.split(";")
        for step in steps:
            step = step.strip()
            step = step.replace(ESCAPED_SEMICOLON, ";")
            if step:
                self.driver.execute(step)

    def run_migration(self, migration, migration_name):
        log.info("Running '%s'." % migration_name)
        start = datetime.datetime.now()
        try:
            self.run_sql_script(migration)
        except ProgrammingError, e:
            raise MigrationSQLError(e, e.args[1])

        self.driver.set_migration_applied(migration_name)

        self.driver.commit()

        end = datetime.datetime.now()
        self.run_times[migration_name] = end - start

    def run_from_file(self, dirname, migration):

        migration_name = os.path.splitext(migration)[0]

        if self.driver.check_migration_applied(migration_name):
            log.info("Skipping '%s'." % migration_name)
            return

        migration_filename = os.path.join(dirname, migration)
        migration = open(migration_filename)

        self.run_migration(migration, migration_name)

        self.end_time = datetime.datetime.now()

    def run_from_dir(self, migrations_dir):

        for migration in sorted(os.listdir(migrations_dir)):
            if not migration.endswith(".sql"):
                continue
            self.run_from_file(migrations_dir, migration)

        self.end_time = datetime.datetime.now()

    def runtime(self):
        return self.end_time - self.start_time


USAGE = """usage: %%prog [options] database migrations_dir

Apply database migrations from migrations_dir to selected database.
migration_dir contains files with .sql extension, that are sorted
and applied.

The applied migrations are saved on a table named  '%s'
in the selected database""" % TABLE_NAME


def main(argv):

    parser = OptionParser(usage=USAGE, version=VERSION)
    parser.add_option("-H", "--host",
                    action="store", dest="host",
                    help="Database server hostname")
    parser.add_option("-u", "--user",
                    action="store", dest="user",
                    help="database username")
    parser.add_option("-p",
                    action="store_true", dest="ask_pass",
                    help="ask for a database password")
    parser.add_option("--password",
                    action="store", dest="password",
                    help="database password")
    parser.add_option("-P", "--port",
                    action="store", dest="port",
                    help="database connection port")
    parser.add_option("-q", "--quiet",
                    action="store_true", dest="quiet", default=False,
                    help="don't print status messages to stdout")
    parser.add_option("-l", "--level",
                    action="store", dest="level", default="info",
                    help="logging level (debug,info,warning,error,critical)")
    parser.add_option("-n", "--noop",
                    action="store_true", dest="noop", default=False,
                    help="Do not run commands.")

    options, args = parser.parse_args(argv)

    LEVELS = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL}

    level = LEVELS.get(options.level.lower())

    if options.quiet:
        level = logging.ERROR

    #"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logging.basicConfig(level=level, format="%(message)s")

    if len(args) == 0:
        parser.error("No database provided")

    if len(args) == 1:
        parser.error("No migrations dir providrd")

    if len(args) > 2:
        parser.error("Too many arguments" + str(args))

    schema = args[0]
    migrations_dir = os.path.abspath(args[1])

    conn_params = {
      "db": schema,
      "cursorclass": DictCursor,
      "use_unicode": True,
      "charset": 'utf8',
      "read_default_file": "~/.my.cnf",
    }
    if options.host:
        conn_params['host'] = options.host

    if options.user:
        conn_params['user'] = options.user

    if options.ask_pass:
        import getpass
        password = getpass.getpass("%s database password : " % schema)
        conn_params['passwd'] = password

    if options.password:
        conn_params['passwd'] = options.password

    if options.port:
        conn_params['port'] = options.port

    try:
        connection = MySQLdb.connect(**conn_params)
    except OperationalError, e:
        log.critical("%s %s" % (e.args[0], e.args[1]))
        sys.exit(2)

    driver = DatabaseDriver(connection, schema, options.noop)
    driver.check_migration_table()

    runner = MigrationRunner(driver)

    try:
        runner.run_from_dir(migrations_dir)
    except MigrationSQLError, e:
        log.critical("SQL ERROR: " + e.message)
        sys.exit(2)
    except OSError, e:
        log.critical("%s : %s" % (e.filename, e.args))
        sys.exit(2)

    log.info("All done in %s." % runner.runtime())

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
