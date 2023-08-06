import datetime, operator

from sqlalchemy import util, sql, schema, exc
from sqlalchemy import types as sqltypes
from sqlalchemy.sql import compiler, expression
from sqlalchemy.engine import base, default, reflection

RESERVED_WORDS = set(['abs', 'acos', 'add', 'add_months', 'after', 'all',
 'alter', 'and', 'any', 'any_user', 'application_context', 'area',
 'array', 'as', 'asc', 'ascii', 'asin', 'atan', 'atan2', 'audit',
 'audit_admin', 'audit_archive', 'audit_insert', 'audit_read',
 'avg', 'before', 'between', 'bigint', 'binary', 'bit', 'blob', 'by',
 'call', 'cascade', 'case', 'cast', 'ceiling', 'char', 'character',
 'character_length', 'chartorowid', 'char_length', 'check', 'chr',
 'clob', 'close', 'clustered', 'coalesce', 'colgroup', 'collate',
 'column', 'commit', 'compress', 'concat', 'connect', 'constraint',
 'contains', 'convert', 'cos', 'count', 'create', 'cross', 'curdate',
 'current', 'current_user', 'currval', 'cursor', 'curtime', 'cycle',
 'database', 'datapages', 'date', 'dayname', 'dayofmonth', 'dayofweek',
 'dayofyear', 'dba', 'db_name', 'dec', 'decimal', 'declare', 'decode',
 'default', 'definition', 'degrees', 'delete', 'desc', 'difference',
 'disconnect', 'distinct', 'double', 'drop', 'each', 'else', 'end',
 'escape', 'event_group', 'exclusive', 'execute', 'exists', 'exp',
 'extent', 'fetch', 'file', 'float', 'floor', 'for', 'foreign', 'from',
 'full', 'grant', 'greatest', 'hash', 'having', 'hour', 'identified',
 'ifnull', 'in', 'index', 'indexpages', 'indicator', 'initcap', 'inner',
 'inout', 'insert', 'instr', 'int', 'integer', 'intersect', 'into',
 'is', 'isolation', 'join', 'key', 'last_day', 'lcase', 'least', 'left',
 'length', 'level', 'like', 'link', 'locate', 'lock', 'log', 'log10',
 'long', 'lower', 'lpad', 'ltrim', 'lvarbinary', 'lvarchar', 'max',
 'maxvalue', 'metadata_only', 'min', 'minus', 'minute', 'minvalue', 'mod',
 'mode', 'modify', 'month', 'monthname', 'months_between', 'national',
 'natural', 'nchar', 'newrow', 'nextval', 'next_day', 'nocompress',
 'nocycle', 'noexecute', 'nolock', 'nomaxvalue', 'nominvalue', 'not',
 'now', 'nowait', 'null', 'nullif', 'nullvalue', 'number', 'numeric',
 'nvl', 'object_id', 'odbcinfo', 'odbc_convert', 'of', 'off',
 'oldrow', 'on', 'open', 'option', 'or', 'out', 'outer', 'pctfree',
 'pi', 'power', 'precision', 'prefix', 'primary', 'privileges',
 'procedure', 'prodefault', 'pro_active', 'pro_array_element',
 'pro_arr_descape', 'pro_arr_escape', 'pro_assign', 'pro_can_create',
 'pro_can_delete', 'pro_can_dump', 'pro_can_load', 'pro_can_read',
 'pro_can_write', 'pro_case_sensitive', 'pro_client_field_trigger',
 'pro_client_file_trigger', 'pro_col_label', 'pro_connect',
 'pro_crc', 'pro_create', 'pro_data_type', 'pro_default_index',
 'pro_delete', 'pro_description', 'pro_dump_name', 'pro_element',
 'pro_enable_64bit_sequences', 'pro_enable_large_keys', 'pro_find',
 'pro_format', 'pro_frozen', 'pro_help', 'pro_hidden', 'pro_label',
 'pro_lob_size_text', 'pro_name', 'pro_odbc',
 'pro_order', 'pro_overrideable', 'pro_procname', 'pro_repl_create',
 'pro_repl_delete', 'pro_repl_write', 'pro_rpos', 'pro_sa_col_label',
 'pro_sa_format', 'pro_sa_help', 'pro_sa_initial', 'pro_sa_label',
 'pro_sa_valmsg', 'pro_server', 'pro_sql_width', 'pro_status',
 'pro_type', 'pro_unified_schema', 'pro_valexp', 'pro_valmsg',
 'pro_view_as', 'pro_word', 'pro_write', 'public', 'quarter',
 'query_timeout', 'radians', 'rand', 'range', 'readpast', 'real', 'recid',
 'references', 'referencing', 'rename', 'repeat', 'replace', 'resource',
 'restrict', 'result', 'return', 'revoke', 'right', 'rollback', 'round',
 'row', 'rowid', 'rowidtochar', 'rownum', 'rpad', 'rtrim', 'schema',
 'searched_case', 'second', 'select', 'sequence', 'sequence_current',
 'sequence_next', 'set', 'share', 'show', 'sign', 'simple_case',
 'sin', 'size', 'smallint', 'some', 'soundex', 'space', 'sql_bigint',
 'sql_binary', 'sql_bit', 'sql_char', 'sql_date', 'sql_decimal',
 'sql_double', 'sql_float', 'sql_integer', 'sql_longvarbinary',
 'sql_longvarchar', 'sql_numeric', 'sql_real', 'sql_smallint', 'sql_time',
 'sql_timestamp', 'sql_tinyint', 'sql_tsi_day', 'sql_tsi_frac_second',
 'sql_tsi_hour', 'sql_tsi_minute', 'sql_tsi_month', 'sql_tsi_quarter',
 'sql_tsi_second', 'sql_tsi_week', 'sql_tsi_year', 'sql_varbinary',
 'sql_varchar', 'sqrt', 'statement', 'statistics', 'storage_attributes',
 'storage_manager', 'store_in_sqleng', 'substr', 'substring', 'suffix',
 'sum', 'suser_name', 'synonym', 'sysdate', 'systime', 'systimestamp',
 'systimestamp_tz', 'systimestamp_utc', 'table', 'tan', 'then',
 'time', 'timestamp', 'timestampadd', 'timestampdiff', 'tinyint', 'to',
 'top', 'to_char', 'to_date', 'to_number', 'to_time', 'to_timestamp',
 'to_timestamp_tz', 'transaction', 'translate', 'trigger', 'type',
 'ucase', 'uid', 'union', 'unique', 'update', 'upper', 'user', 'user_id',
 'user_name', 'using', 'values', 'vararray', 'varbinary', 'varchar',
 'varying', 'view', 'wait', 'week', 'when', 'where', 'with', 'work',
 'year', 'zone'])

from sqlalchemy.types import INTEGER, VARCHAR, CHAR, TEXT, FLOAT, NUMERIC, \
    TIMESTAMP, TIME, DATE, BOOLEAN, BIGINT

ischema_names = {
        'bigint':BIGINT,
        'bit':BOOLEAN,
        'character':CHAR,
        'date':DATE,
        'float':FLOAT, # double precision. Also FLOAT(8) in SQL.
        'integer':INTEGER,
        'numeric':NUMERIC,
        'real':FLOAT, # single precision. Also FLOAT(4) in SQL.
        'smallint':INTEGER, # 16 bits, signed
        'time':TIME,
        'tinyint':INTEGER, # 8 bits, signed
        'timestamp':TIMESTAMP,
        'timestamp_timezone':TIMESTAMP,
        'varbinary':VARCHAR,
        'varchar':VARCHAR,
}

class ProgressExecutionContext(default.DefaultExecutionContext):
    pass

class ProgressTypeCompiler(compiler.GenericTypeCompiler):
    pass

class ProgressSQLCompiler(compiler.SQLCompiler):
    def get_select_precolumns(self, select):
        s = select._distinct and "DISTINCT " or ""
        if select._limit:
            s += "TOP %s " % (select._limit,)
            return s
        return compiler.SQLCompiler.get_select_precolumns(self, select)

    def limit_clause(self, select):
        return ""

class ProgressDDLCompiler(compiler.DDLCompiler):
    pass

class ProgressIdentifierPreparer(compiler.IdentifierPreparer):
    reserved_words = RESERVED_WORDS

class ProgressDialect(default.DefaultDialect):
    name = 'progress'
    supports_unicode_statements = True
    supports_sane_rowcount = False
    supports_sane_multi_rowcount = False
    colspecs = {}

    type_compiler = ProgressTypeCompiler
    statement_compiler = ProgressSQLCompiler
    ddl_compiler = ProgressDDLCompiler
    preparer = ProgressIdentifierPreparer

    schema_name = "pub"

    def __init__(self, **params):
        super(ProgressDialect, self).__init__(**params)
        self.text_as_varchar = False

    def _check_unicode_returns(self, connection):
        return True

        # XXX Lately this hangs the database:
        cursor = self._get_raw_cursor(connection)
        item = cursor.columns('SYSTABLES').fetchone()
        try:
            item[1].encode('ascii')
        except UnicodeEncodeError, e:
            # In Linux, if the connection has been opened with
            # unicode_results=True and an unpatched pyodbc (see
            # progress_sa distribution) then the Progress ODBC driver
            # returns UTF-8 interpreted by pyodbc as UCS-2.
            # Things go downhill from there unless we abort.
            raise exc.SQLAlchemyError(
                "Non-ASCII in SYSTABLES. "
                "Are you using an unpatched pyodbc?", 
                )

        cursor.execute(
            str(
                expression.select( 
                [expression.cast(
                    expression.literal_column("'test unicode returns'"),sqltypes.VARCHAR(60))
                ]).compile(dialect=self)
            ) + " FROM SYSPROGRESS.SYSTABLES" # requires FROM a_real_table
        )
        row = cursor.fetchone()
        result = isinstance(row[0], unicode)
        cursor.close()

        return result


    def last_inserted_ids(self):
        return self.context.last_inserted_ids

    def get_default_schema_name(self, connection):
        return self.schema_name

    def _get_raw_cursor(self, connection):
        return connection.engine.raw_connection().cursor()

    def get_table_names(self, connection, schema):
        cursor = self._get_raw_cursor(connection)
        s = cursor.tables(schema=schema or '')
        return [row.table_name for row in s]

    def has_table(self, connection, tablename, schema=None):
        cursor = self._get_raw_cursor(connection)
        s = cursor.tables(table=tablename, schema=schema or '')
        return s.fetchone() is not None

    def get_columns(self, connection, table_name, schema=None, **kw):
        columns = []
        cursor = self._get_raw_cursor(connection)
        results = cursor.columns(table_name, schema=schema or '')
        index = dict((x[1][0], x[0]) for x in enumerate(cursor.description))
        for column in results:
            name = column[index['column_name']]
            nullable = bool(column[index['nullable']])
            default = column[index['column_def']]
            autoincrement = False

            type_name = column[index['type_name']]
            column_size = column[index['column_size']]
            coltype = ischema_names[type_name](column_size)

            columns.append(dict(name=name, type=coltype,
                nullable=nullable, default=default,
                autoincrement=autoincrement))

        return columns

    def get_primary_keys(self, connection, table_name, schema=None, **kw):
        c = self._get_raw_cursor(connection)
        pk = [r[3] for r in c.primaryKeys(table_name, schema=schema or '').fetchall()]
        return pk

    def get_foreign_keys(self, *args, **kw):
        # does not seem to be implemented in the database.
        return []

    def get_indexes(self, connection, table_name, schema=None, **kw):
        # implemented in the database, not terribly useful.
        # would be a list of dict(name='', column_names=[], unique=)...
        return []

