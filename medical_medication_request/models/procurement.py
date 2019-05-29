from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(
        self, product_id, product_qty, product_uom, location_id, name,
        origin, values, group_id
    ):
        res = super()._get_stock_move_values(
            product_id, product_qty, product_uom, location_id, name,
            origin, values, group_id
        )
        if values.get('medication_administration_id', False):
            res['medication_administration_id'] = values.get(
                'medication_administration_id')
        return res
