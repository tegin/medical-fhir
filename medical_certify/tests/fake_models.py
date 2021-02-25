from odoo import fields, models


class MedicalCertify(models.Model):
    _name = "medical.certify.demo"
    _inherit = "digest.base"

    name = fields.Char(required=True)

    def _generate_serializer(self):
        result = super(MedicalCertify, self)._generate_serializer()
        result["name"] = self.name
        return result
