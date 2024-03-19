# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from odoo import fields, models


class MedicalPatientPartner(models.Model):
    # FHIR Entity: Patient (http://hl7.org/fhir/patient.html)
    _name = "medical.patient.partner"
    _description = "Medical Patient Partner"
    _inherits = {"res.partner": "partner_id"}  # , "medical.patient": "patient_id"}

    partner_id = fields.Many2one("res.partner", required=True, ondelete="restrict")
    patient_id = fields.Many2one("medical.patient", required=True, ondelete="")
    partner_type = fields.Selection(
        [("f", "Family"), ("r", "Responsible")], required=True
    )

    _sql_constraints = [
        (
            "partner_uniq",
            "UNIQUE(partner_id, patient_id)",
            "This partner is already added!",
        )
    ]
