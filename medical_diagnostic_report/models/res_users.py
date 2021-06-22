from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"
    digital_signature = fields.Binary(attachment=True)
