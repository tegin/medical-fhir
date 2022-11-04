# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    encounter_id = fields.Many2one(
        comodel_name="medical.encounter", ondelete="restrict", index=True
    )

    @api.constrains("patient_id", "encounter_id")
    def _check_patient_encounter(self):
        if self.env.context.get("no_check_patient", False):
            return
        for record in self.filtered(lambda r: r.encounter_id):
            if record.encounter_id.patient_id != record.patient_id:
                raise ValidationError(
                    _("Inconsistency between patient and encounter")
                )

    def _get_parents(self):
        res = super()._get_parents()
        res.append(self.encounter_id)
        return res
