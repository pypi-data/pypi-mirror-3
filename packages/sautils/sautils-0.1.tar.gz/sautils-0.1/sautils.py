"""

    sautils -- SQLAlchemy utilities
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Various SQLAlchemy utilities which are a little specific to be proposed to
    main SQLAlchemy distribution.

"""

from sqlalchemy.ext.compiler import compiles
from sqlalchemy import select, and_, literal
from sqlalchemy.sql.expression import Executable, ClauseElement, Alias

__all__ = ('insert_from_select', 'upsert_from_select', 'upsert')

class InsertFromSelect(Executable, ClauseElement):
    """ Insert from select"""

    def __init__(self, table, select, *fields):
        self.table = table
        self.select = select
        self.fields = fields

@compiles(InsertFromSelect)
def visit_insert_from_select(element, compiler, **kw):
    if element.fields:
        f = ' (%s) ' % ', '.join(element.fields)
    else:
        f = ' '
    return 'INSERT INTO %s%s(%s)' % (
        compiler.process(element.table, asfrom=True),
        f,
        compiler.process(element.select)
    )

insert_from_select = InsertFromSelect

def upsert_from_select(table, q, *fields):
    """ Upsert from select"""
    sq = q.alias('__q')
    pks = table.primary_key.columns
    q = (select([sq])
        .select_from(sq.outerjoin(table,and_(*(sq.c[c.key] == c for c in pks))))
        .where(list(pks)[0] == None))
    return insert_from_select(table, q, *fields)

def upsert(table, **values):
    """ Upsert"""
    values = values.items()
    fields = [k for (k, v) in values]
    return upsert_from_select(
        table, select([literal(v).label(k) for (k, v) in values]), *fields)
