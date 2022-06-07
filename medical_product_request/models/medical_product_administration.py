# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalProductAdministration(models.Model):

    _name = "medical.product.administration"
    _description = "Medical Product Administration"
    _inherit = ["medical.abstract", "mail.thread", "mail.activity.mixin"]
    _rec_name = "internal_identifier"

    name = fields.Char()

    internal_identifier = fields.Char(string="Product Administration")

    product_request_id = fields.Many2one(
        comodel_name="medical.product.request"
    )

    state = fields.Selection(
        selection=[
            ("in_progress", "In_progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="in_progress",
    )
    # Fhir Concept: status

    product_type = fields.Selection(
        related="medical_product_template_id.product_type"
    )

    medical_product_template_id = fields.Many2one(
        comodel_name="medical.product.template"
    )
    # Fhir Concept: medication

    product_type = fields.Selection(
        related="medical_product_template_id.product_type"
    )
    # Used for visualization purposes

    patient_id = fields.Many2one(related="product_request_id.patient_id")
    # Fhir Concept: Subject

    encounter_id = fields.Many2one(related="product_request_id.encounter_id")
    # Fhir concept: encounter

    quantity_administered = fields.Float(required=True)
    quantity_administered_uom_id = fields.Many2one(
        required=True, comodel_name="uom.uom"
    )

    quantity_uom_domain = fields.Char(compute="_compute_quantity_uom_domain")

    administration_date = fields.Datetime(copy=False)
    administration_user_id = fields.Many2one(
        comodel_name="res.users", copy=False
    )
    # Fhir Concept: performer

    cancel_date = fields.Datetime(copy=False)
    cancel_user_id = fields.Many2one(comodel_name="res.users", copy=False)

    comments = fields.Text()

    @api.depends("medical_product_template_id")
    def _compute_quantity_uom_domain(self):
        for rec in self:
            domain = []
            if rec.medical_product_template_id:
                domain.append(("measure_type", "=", "unit"))
                if rec.medical_product_template_id.form_id:
                    domain.insert(0, "|")
                    domain.append(
                        (
                            "id",
                            "in",
                            rec.medical_product_template_id.form_id.uom_ids.ids,
                        )
                    )
            else:
                domain = [("id", "=", 0)]
            rec.quantity_uom_domain = json.dumps(domain)

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code(
                "medical.product.administration"
            )
            or "/"
        )

    @api.constrains("quantity_administered")
    def _check_quantity_administered(self):
        for rec in self:
            if rec.quantity_administered < 1:
                raise ValidationError(
                    _("Quantity administrated must be positive")
                )

    def _complete_administration_vals(self):
        return {
            "state": "completed",
            "administration_date": fields.Datetime.now(),
            "administration_user_id": self.env.user.id,
        }

    def complete_administration_action(self):
        self.ensure_one()
        self.write(self._complete_administration_vals())

    def _cancel_vals(self):
        return {
            "state": "cancelled",
            "cancel_user_id": self.env.user.id,
            "cancel_date": fields.Datetime.now(),
        }

    def cancel_action(self):
        self.ensure_one()
        self.write(self._cancel_vals())
