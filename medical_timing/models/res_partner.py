# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    timing_qd = fields.Float()
    timing_am = fields.Float()
    timing_pm = fields.Float()
    timing_bid_1 = fields.Float()
    timing_bid_2 = fields.Float()
    timing_tid_1 = fields.Float()
    timing_tid_2 = fields.Float()
    timing_tid_3 = fields.Float()
    timing_qid_1 = fields.Float()
    timing_qid_2 = fields.Float()
    timing_qid_3 = fields.Float()
    timing_qid_4 = fields.Float()
