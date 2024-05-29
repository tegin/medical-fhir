from odoo import models


class IrActionsActWindowPagePrev(models.AbstractModel):
    _name = "ir.actions.impression.select_record"
    _description = "Action to page to the previous record from a form view button"

    def _get_readable_fields(self):
        return set()  # pragma: no cover
