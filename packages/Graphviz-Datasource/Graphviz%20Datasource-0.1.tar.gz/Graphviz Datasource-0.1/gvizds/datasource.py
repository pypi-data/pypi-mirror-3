import gviz_api
import copy
import json

import gvizds.parser as parser


class Parameters(dict):

    def __init__(self, tqx_string):
        super(Parameters, self).__init__()
        if tqx_string:
            for s in tqx_string.split(';'):
                k, v = s.split(':')
                self[k] = v


def format_column_name(*args):
    return '_'.join(args).lower().replace(' ', '_')


def format_responses(desc, query, order, data, req_id=0):
    if query.pivot:
        pivot_col = query.pivot[0].column
        cols = set([r[pivot_col] for r in data])
        group_cols = [c.column for c in query.group_by]
        data_cols = filter(
                lambda x: x not in group_cols,
                [c.column for c in query.columns]
            )

        order = list(group_cols)
        rows = {}
        for d in data:
            # create key based on group by columns
            key = tuple([d[k] for k in group_cols])
            # get existing row for key
            row = rows.get(key) or dict([(k, d[k]) for k in group_cols])
            # set value for column names
            pivot_val = d[pivot_col]
            for col in data_cols:
                col_name = format_column_name(col, pivot_val)
                row[col_name] = d.get(col)
                if col_name not in desc:
                    desc[col_name] = (
                            desc[col][0],
                            pivot_val + ' ' + desc[col][1]
                            )
                if col_name not in order:
                    order.append(col_name)
            # create column name(s) based on pivot_col_value + data_col_name
            # update_desc for column
            rows[key] = row

        data = sorted([
            v for k, v in rows.items()],
            key=lambda x: x[group_cols[0]]
            )

    data_table = gviz_api.DataTable(desc)
    data_table.LoadData(data)
    return data_table.ToJSonResponse(
        req_id=req_id,
        columns_order=order,
    )


class DataSource(object):

    def __init__(self, config):
        self.config = config

    def query(self, table, tq=None, tqx=None):
        params = Parameters(tqx)

        desc_plain = copy.copy(self.config.get_table(table))
        desc = {}
        for k, v in desc_plain.items():
            desc[k] = tuple(v)

        if not tq:
            tq = 'select ' + (','.join(desc.keys()))

        query = parser.Query(tq)

        sql = query.sql(table)
        with self.config.get_db() as db:
            try:
                cur = db.cursor()
                cur.execute(sql)
            except Exception as e:
                error_obj = {
                    'status': 'error',
                    'errors': [{
                        'reason': 'invalid_query',
                        'message': str(e)
                    }],
                    'reqId': params.get('reqId', 0)
                }
                return 'google.visualization.Query.setResponse(%s);' \
                        % json.dumps(error_obj)
            col_desc = [col[0] for col in cur.description]

        for k in desc.keys():
            if k not in col_desc:
                del desc[k]

        data = []
        for row in cur.fetchall():
            d = dict(zip(col_desc, [v for v in row]))
            for x in [x for x in d if d[x] == 'None']:
                d.pop(x)
            for k, v in d.items():
                d[k] = self.config.fix_value(desc[k][0], v)
            data.append(d)

        req_id = params.get('reqId', 0)

        return format_responses(desc, query, col_desc, data, req_id)
