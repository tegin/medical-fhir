# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalCareplanMedicalWizardState(models.Model):

    _name = "medical.careplan.medical.wizard.state"
    _description = "Medical Careplan Medical Wizard State"

    name = fields.Char()

    done = fields.Boolean()
    only_timing = fields.Boolean()
