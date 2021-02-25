from odoo import fields, models


class MedicalSignCertify(models.Model):
    _name = "medical.certify.sign.demo"
    _inherit = "certify.base"

    name = fields.Char(required=True)

    def _generate_serializer(self):
        result = super()._generate_serializer()
        result["name"] = self.name
        return result
