#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields
from trytond.wizard import Wizard
from trytond.pyson import PYSONEncoder


class ProductCostHistory(ModelSQL, ModelView):
    'History of Product Cost'
    _name = 'product.product.cost_history'
    _description = __doc__
    _rec_name = 'date'

    template = fields.Many2One('product.template', 'Product')
    date = fields.DateTime('Date')
    cost_price = fields.Numeric('Cost Price')

    def __init__(self):
        super(ProductCostHistory, self).__init__()
        self._order.insert(0, ('date', 'DESC'))

    def table_query(self, context=None):
        property_obj = self.pool.get('ir.property')
        return ('SELECT ' \
                    'MAX(__id) AS id, ' \
                    'MAX(create_uid) AS create_uid, ' \
                    'MAX(create_date) AS create_date, ' \
                    'MAX(write_uid) AS write_uid, ' \
                    'MAX(write_date) AS write_date, ' \
                    'COALESCE(write_date, create_date) AS date, ' \
                    'CAST(TRIM(\',\' FROM SUBSTRING(res FROM \',.*\')) AS INTEGER) ' \
                        'AS template, ' \
                    'CAST(TRIM(\',\' FROM value) AS NUMERIC) AS cost_price ' \
                'FROM "' + property_obj._table + '__history" ' \
                'WHERE name = \'cost_price\' ' \
                    'AND res LIKE \'product.template,%%\' ' \
                'GROUP BY id, COALESCE(write_date, create_date), res, value',
                [])

ProductCostHistory()


class OpenProductCostHistory(Wizard):
    'Open Product Cost History'
    _name = 'product.product.cost_history.open'
    states = {
        'init': {
            'result': {
                'type': 'action',
                'action': '_open',
                'state': 'end',
            },
        },
    }

    def _open(self, cursor, user, data, context=None):
        model_data_obj = self.pool.get('ir.model.data')
        act_window_obj = self.pool.get('ir.action.act_window')
        product_obj = self.pool.get('product.product')
        act_window_id = model_data_obj.get_id(cursor, user,
                'product_cost_history', 'act_product_cost_history_form',
                context=context)
        res = act_window_obj.read(cursor, user, act_window_id, context=context)

        if not data['id'] or data['id'] < 0:
            res['pyson_domain'] = PYSONEncoder().encode([
                ('template', '=', False),
            ])
        else:
            product = product_obj.browse(cursor, user, data['id'], context=context)
            res['pyson_domain'] = PYSONEncoder().encode([
                ('template', '=', product.template.id),
            ])
        return res

OpenProductCostHistory()
