from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"
    digital_signature = fields.Binary(attachment=True)

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ["digital_signature"]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ["digital_signature"]
