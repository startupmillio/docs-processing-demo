import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import text

from db import persistent_engine as engine

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
)
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir)
    )
)
sys.path.append(os.getcwd())

from alembic import context

from config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.

config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from models.base import Model

target_metadata = Model.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

psql_url = "postgresql+asyncpg://{username}:{password}@{host}:{port}/{dbname}".format(
    username=settings.DATABASE_USER,
    password=settings.DATABASE_PASSWORD,
    host=settings.DATABASE_HOST,
    port=settings.DATABASE_PORT,
    dbname=settings.DATABASE_DB,
)


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=psql_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # compare_type=True,
        # render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # compare_type=True,
        # render_as_batch=True,
    )

    with context.begin_transaction():
        connection.execute(text("SELECT pg_advisory_xact_lock(10000);"))
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
