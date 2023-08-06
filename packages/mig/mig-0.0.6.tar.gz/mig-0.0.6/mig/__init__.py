# mig - SQLAlchemy migrations
# Copyright 2012  mig contributors.  See NOTICE
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from sqlalchemy.orm import sessionmaker
from mig.util import simple_printer

_log = logging.getLogger(__name__)


def run(engine, name, models, migrations):
    dbdata = DatabaseData(name, models, migrations)

    Session = sessionmaker(bind=engine)

    manager = dbdata.make_migration_manager(Session())
    manager.init_or_migrate()


class DatabaseData(object):
    def __init__(self, name, models, migrations):
        self.name = name
        self.models = models
        self.migrations = migrations

    def make_migration_manager(self, session):
        return MigrationManager(
            self.name, self.models, self.migrations, session)


class MigrationManager(object):
    """
    Migration handling tool.

    Takes information about a database, lets you update the database
    to the latest migrations, etc.
    """

    def __init__(self, name, models, migration_registry, session,
                 printer=simple_printer):
        """
        Args:
         - name: identifier of this section of the database
         - session: session we're going to migrate
         - migration_registry: where we should find all migrations to
           run
        """
        self.name = name
        self.models = models
        self.session = session
        self.migration_registry = migration_registry
        self._sorted_migrations = None
        self.printer = printer

        # For convenience
        from mig.models import MigrationData

        self.migration_model = MigrationData
        self.migration_table = MigrationData.__table__

    @property
    def sorted_migrations(self):
        """
        Sort migrations if necessary and store in self._sorted_migrations
        """
        if not self._sorted_migrations:
            self._sorted_migrations = sorted(
                self.migration_registry.items(),
                # sort on the key... the migration number
                key=lambda migration_tuple: migration_tuple[0])

        return self._sorted_migrations

    @property
    def migration_data(self):
        """
        Get the migration row associated with this object, if any.
        """
        return self.session.query(
            self.migration_model).filter_by(name=self.name).first()

    @property
    def latest_migration(self):
        """
        Return a migration number for the latest migration, or 0 if
        there are no migrations.
        """
        if self.sorted_migrations:
            return self.sorted_migrations[-1][0]
        else:
            # If no migrations have been set, we start at 0.
            return 0

    @property
    def database_current_migration(self):
        """
        Return the current migration in the database.
        """
        # If the table doesn't even exist, return None.
        if not self.migration_table.exists(self.session.bind):
            return None

        # Also return None if self.migration_data is None.
        if self.migration_data is None:
            return None

        return self.migration_data.version

    def set_current_migration(self, migration_number=None):
        """
        Set the migration in the database to migration_number
        (or, the latest available)
        """
        self.migration_data.version = migration_number or self.latest_migration
        self.session.commit()

    def migrations_to_run(self):
        """
        Get a list of migrations to run still, if any.

        Note that this will fail if there's no migration record for
        this class!
        """
        assert self.database_current_migration is not None

        db_current_migration = self.database_current_migration

        return [
            (migration_number, migration_func)
            for migration_number, migration_func in self.sorted_migrations
            if migration_number > db_current_migration]

    def init_tables(self):
        """
        Create all tables relative to this package
        """
        # sanity check before we proceed, none of these should be created
        for model in self.models:
            # Maybe in the future just print out a "Yikes!" or something?
            _log.debug('Checking for table {0}'.format(model))
            assert not model.__table__.exists(self.session.bind)

        _log.debug('Creating {0}'.format(self.models))
        self.migration_model.metadata.create_all(
            self.session.bind,
            tables=[model.__table__ for model in self.models])

    def create_new_migration_record(self):
        """
        Create a new migration record for this migration set
        """
        migration_record = self.migration_model(
            name=self.name,
            version=self.latest_migration)
        self.session.add(migration_record)
        self.session.commit()

    def dry_run(self):
        """
        Print out a dry run of what we would have upgraded.
        """
        if self.database_current_migration is None:
            self.printer(
                    u'~> Woulda initialized: %s\n' % self.name_for_printing())
            return u'inited'

        migrations_to_run = self.migrations_to_run()
        if migrations_to_run:
            self.printer(
                u'~> Woulda updated %s:\n' % self.name_for_printing())

            for migration_number, migration_func in migrations_to_run():
                self.printer(
                    u'   + Would update %s, "%s"\n' % (
                        migration_number, migration_func.func_name))

            return u'migrated'

    def name_for_printing(self):
        if self.name == u'__main__':
            return u"main mediagoblin tables"
        else:
            # TODO: Use the friendlier media manager "human readable" name
            return u'media type "%s"' % self.name

    def init_or_migrate(self):
        """
        Initialize the database or migrate if appropriate.

        Returns information about whether or not we initialized
        ('inited'), migrated ('migrated'), or did nothing (None)
        """
        assure_migrations_table_setup(self.session)

        # Find out what migration number, if any, this database data is at,
        # and what the latest is.
        migration_number = self.database_current_migration

        # Is this our first time?  Is there even a table entry for
        # this identifier?
        # If so:
        #  - create all tables
        #  - create record in migrations registry
        #  - print / inform the user
        #  - return 'inited'
        if migration_number is None:
            self.printer(u"-> Initializing %s... " % self.name_for_printing())

            self.init_tables()
            # auto-set at latest migration number
            self.create_new_migration_record()

            self.printer(u"done.\n")
            self.set_current_migration()
            return u'inited'

        # Run migrations, if appropriate.
        migrations_to_run = self.migrations_to_run()
        if migrations_to_run:
            self.printer(
                u'-> Updating %s:\n' % self.name_for_printing())
            for migration_number, migration_func in migrations_to_run:
                self.printer(
                    u'   + Running migration %s, "%s"... ' % (
                        migration_number, migration_func.func_name))
                migration_func(self.session)
                self.printer('done.\n')

            self.set_current_migration()
            return u'migrated'

        # Otherwise return None.  Well it would do this anyway, but
        # for clarity... ;)
        return None


class RegisterMigration(object):
    """
    Tool for registering migrations

    Call like:

    @RegisterMigration(33)
    def update_dwarves(database):
        [...]

    This will register your migration with the default migration
    registry.  Alternately, to specify a very specific
    migration_registry, you can pass in that as the second argument.

    Note, the number of your migration should NEVER be 0 or less than
    0.  0 is the default "no migrations" state!
    """
    def __init__(self, migration_number, migration_registry):
        assert migration_number > 0, "Migration number must be > 0!"
        assert migration_number not in migration_registry, \
            "Duplicate migration numbers detected!  That's not allowed!"

        self.migration_number = migration_number
        self.migration_registry = migration_registry

    def __call__(self, migration):
        self.migration_registry[self.migration_number] = migration
        return migration


def assure_migrations_table_setup(db):
    """
    Make sure the migrations table is set up in the database.
    """
    from mig.models import MigrationData

    if not MigrationData.__table__.exists(db.bind):
        MigrationData.metadata.create_all(
            db.bind, tables=[MigrationData.__table__])
