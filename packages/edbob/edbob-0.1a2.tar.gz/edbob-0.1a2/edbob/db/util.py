#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  edbob -- Pythonic Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of edbob.
#
#  edbob is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  edbob is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with edbob.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
``edbob.db.util`` -- Database Utilities
"""

import os.path

import sqlalchemy.exc
# import migrate.versioning.api
# import migrate.exceptions

# import rattail
# from rattail.db import exc as exceptions
# from rattail.db import Session
# from rattail.db.classes import Role
# from rattail.db.model import get_metadata
# from rattail.db.perms import get_administrator

import edbob.db
from edbob.db import exceptions
from edbob.db.model import Base
# from edbob.db.model import get_metadata


# def core_schema_installed(engine=None):
#     """
#     Returns boolean indicating whether or not the core schema has been
#     installed to the database represented by ``engine``.  If ``engine`` is not
#     provided, then ``rattail.engine`` will be assumed.
#     """
    
#     if engine is None:
#         engine = rattail.engine

#     try:
#         get_database_version(engine)
#     except exceptions.CoreSchemaNotInstalled:
#         return False
#     return True


# def get_database_version(engine=None, extension=None):
#     """
#     Returns a SQLAlchemy-Migrate version number found in the database
#     represented by ``engine``.

#     If no engine is provided, :attr:`edbob.db.engine` is assumed.

#     If ``extension`` is provided, the version for its schema is returned;
#     otherwise the core schema is assumed.
#     """

#     if engine is None:
#         engine = edbob.db.engine

#     try:
#         version = migrate.versioning.api.db_version(
#             str(engine.url), get_repository_path(extension))

#     except (sqlalchemy.exc.NoSuchTableError,
#             migrate.exceptions.DatabaseNotControlledError):
#         raise exceptions.CoreSchemaNotInstalled(engine)

#     return version


def get_repository_path(extension=None):
    """
    Returns the absolute filesystem path to the SQLAlchemy-Migrate repository
    for ``extension``.

    If no extension is provided, ``edbob``'s core repository is assumed.
    """

    if not extension:
        from edbob.db import schema
        return os.path.dirname(schema.__file__)

    return os.path.dirname(extension.schema.__file__)

    
# def get_repository_version(extension=None):
#     """
#     Returns the version of the SQLAlchemy-Migrate repository for ``extension``.

#     If no extension is provided, ``edbob``'s core repository is assumed.
#     """

#     return migrate.versioning.api.version(get_repository_path(extension))


def install_core_schema(engine=None):
    """
    Installs the core schema to the database represented by ``engine``.

    If no engine is provided, :attr:`edbob.db.engine` is assumed.
    """

    if not engine:
        engine = edbob.db.engine

    # Attempt connection in order to force an error, if applicable.
    conn = engine.connect()
    conn.close()

    # # Check DB version to see if core schema is already installed.
    # try:
    #     db_version = get_database_version(engine)
    # except exceptions.CoreSchemaNotInstalled:
    #     pass
    # else:
    #     raise exceptions.CoreSchemaAlreadyInstalled(db_version)

    # Create tables for core schema.
    # metadata = get_metadata()
    # Base.metadata.create_all(engine)
    meta = edbob.db.get_core_metadata()
    meta.create_all(engine)

    # # Add versioning for core schema.
    # migrate.versioning.api.version_control(
    #     str(engine.url), get_repository_path(), get_repository_version())

    # WTF
    # session = Session(bind=engine)
    # get_administrator(session)
    # session.commit()
    # session.close()


# def upgrade_schema(extension=None, engine=None):
#     """
#     Upgrades a schema within the database represented by ``engine`` (or
#     ``rattail.engine`` if none is provided).  If ``extension`` is provided,
#     then its schema will be upgraded; otherwise the core is assumed.
#     """

#     if engine is None:
#         engine = rattail.engine
#     repo_version = get_repository_version(extension)
#     db_version = get_database_version(engine, extension)
#     if db_version < repo_version:
#         migrate.versioning.api.upgrade(str(engine.url), get_repository_path(extension), repo_version)
