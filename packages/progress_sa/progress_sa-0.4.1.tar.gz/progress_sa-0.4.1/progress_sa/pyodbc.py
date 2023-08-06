from progress_sa.base import ProgressDialect, ProgressExecutionContext
from sqlalchemy.connectors.pyodbc import PyODBCConnector
from sqlalchemy.util import asbool

class ProgressExecutionContext_pyodbc(ProgressExecutionContext):
    pass

class Progress_pyodbc(PyODBCConnector, ProgressDialect):
    # For OpenEdge 10. Progress 9 uses Progress_SQL92_Driver.
    pyodbc_driver_name = 'Progress_SQL_Driver'
    execution_ctx_cls = ProgressExecutionContext_pyodbc

    def __init__(self, description_encoding='latin-1', **params):
        super(Progress_pyodbc, self).__init__(**params)
        self.description_encoding = description_encoding

dialect = Progress_pyodbc
