from progress_sa import base, pyodbc

# default dialect
base.dialect = pyodbc.dialect

from base import dialect

__all__ = ['dialect']
