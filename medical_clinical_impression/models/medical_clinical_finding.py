# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalClinicalFinding(models.Model):

    _inherit = "medical.clinical.finding"

    create_condition_from_clinical_impression = fields.Boolean(
        help="If marked, "
        "when this clinical finding is added to a clinical impression,"
        "it will create automatically a condition for the corresponding patient"
    )
