# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalRequestSetTiming(models.TransientModel):

    _name = "medical.request.set.timing"
    _description = "Set timing"

    res_model = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    timing_id = fields.Many2one("medical.timing", required=True)
    location_id = fields.Many2one(
        "res.partner",
        domain=[("is_location", "=", True)],
        required=True,
        readonly=True,
    )
    start_date = fields.Datetime(required=True, default=fields.Datetime.now)
    next_expected_date = fields.Datetime(compute="_compute_next_expected_date")

    @api.depends("timing_id", "start_date")
    def _compute_next_expected_date(self):
        for record in self:
            record.next_expected_date = record.timing_id._closest_next_date(
                record.start_date, record.location_id
            )

    def configure_timing(self):
        self.ensure_one()
        self._configure_timing()
        return {}

    def _configure_timing_vals(self):
        return {
            "next_expected_date": self.next_expected_date,
            "timing_id": self.timing_id.id,
            "timing_start_date": self.start_date,
        }

    def _configure_timing(self):
        obj = self.env[self.res_model].browse(self.res_id)
        obj.write(self._configure_timing_vals())
        return obj
