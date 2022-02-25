from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"
    digital_signature = fields.Binary(attachment=True)

    def __init__(self, pool, cr):  # pylint: disable=E0101
        """ Override of __init__ to add access rights.
            Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """

        hr_writable_fields = [
            "digital_signature",
        ]

        init_res = super().__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = (
            type(self).SELF_READABLE_FIELDS + hr_writable_fields
        )
        type(self).SELF_WRITEABLE_FIELDS = (
            type(self).SELF_WRITEABLE_FIELDS + hr_writable_fields
        )
        return init_res
