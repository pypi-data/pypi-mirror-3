from pyparsing import Combine, Keyword, Group, Word, Forward, Optional, \
        Literal, ZeroOrMore, \
        alphas, alphanums, nums, delimitedList, oneOf, quotedString


class Query(object):

    def __init__(self, query_str):
        tokens = _gvis_stmt.parseString(query_str)
        self.tokens = tokens
        self.columns = tokens.columns
        self.where = tokens.where
        self.group_by = tokens.group_by
        self.pivot = tokens.pivot

    @classmethod
    def _column(clazz, c):
        if isinstance(c, str):
            return c
        if c.function:
            return "%(function)s(%(column)s) as %(column)s" % c
        return c.column

    def sql(self, table):
        sql = ['select']

        pivot_cols = []
        if self.pivot:
            pivot_cols = [Query._column(c) for c in self.pivot]

        columns = pivot_cols + [Query._column(c) for c in self.columns]

        sql.append(', '.join(columns))
        sql.append('from')
        sql.append(table)

        if self.where:
            sql.append('where')
            for token in self.where:
                if isinstance(token, (unicode, str)):
                    sql.append(token)
                else:
                    where_tokens = []
                    for t in token:
                        if isinstance(t, (unicode, str)):
                            where_tokens.append(t)
                        else:
                            where_tokens.append(', '.join(t))
                    sql.append(' '.join(where_tokens))

        if self.group_by or self.pivot:
            sql.append('group by')
            columns = []
            if self.pivot:
                columns = columns + [Query._column(c) for c in self.pivot]
            if self.group_by:
                columns = columns + [Query._column(c) for c in self.group_by]
            sql.append(', '.join(columns))
        
        return ' '.join(sql)

def _get_parser():
    gvis_stmt = Forward()

    op = (oneOf("= != < > >= <=") | Keyword("in") | Keyword("not in")) 

    aggreg_functions = (
        Literal("sum") |
        Literal("ave") |
        Literal("max") |
        Literal("min") |
        Literal("count")
    )

    column = Word(alphas+'_').setResultsName('column')
    column_expr = Group(aggreg_functions.setResultsName('function') + Literal("(") + column + Literal(")")) | Group(column)
    columns = delimitedList(column_expr)

    value = (Word(alphanums+'-')|quotedString) | Literal("(") + Group(delimitedList(
            Word(alphanums+'-') | quotedString
        )) + Literal(")")

    expr = Group(column + op + value)

    exprs = Forward()
    exprs << expr + ZeroOrMore((Keyword("and") | Keyword("or")) + exprs)

    gvis_stmt << (
        Keyword("select", caseless=True) +
        ( '*' | Group(columns)).setResultsName('columns') +
        Optional(
            Keyword("where", caseless=True) +
            (exprs).setResultsName('where')
        ) +
        Optional(
            Keyword("group by", caseless=True) +
            Group(columns).setResultsName('group_by')
        ) +
        Optional(
            Keyword("pivot", caseless=True) +
            Group(columns).setResultsName('pivot')
        )
    )
    return gvis_stmt

_gvis_stmt = _get_parser()

