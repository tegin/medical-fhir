# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.osv import expression


class MedicalAbstractConcept(models.AbstractModel):
    # FHIR Entity: Medical Code system concept
    # (https://www.hl7.org/fhir/codesystem.html)
    _name = "medical.abstract.concept"
    _description = "Medical abstract concept"

    code = fields.Char(required=True, index=True)  # FHIR Field: code
    name = fields.Char(required=True)  # FHIR Field: display
    definition = fields.Char()  # FHIR Field: definition
    editable = fields.Boolean(default=True)

    @api.depends("name", "code")
    def name_get(self):
        result = []
        for record in self:
            name = "[%s]" % record.code
            if record.name:
                name = "{} {}".format(name, record.name)
            result.append((record.id, name))
        return result

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                "|",
                ("code", "=ilike", name + "%"),
                ("name", operator, name),
            ]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ["&", "!"] + domain[1:]
        accounts = self.search(domain + args, limit=limit)
        return accounts.name_get()
