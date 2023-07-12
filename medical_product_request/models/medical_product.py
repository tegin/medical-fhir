# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalProductTemplate(models.Model):

    _name = "medical.product.template"
    _description = "Medical Product Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name_template"

    name_template = fields.Char(
        compute="_compute_medical_product_name", store=True
    )

    name = fields.Char(required=True)

    product_ids = fields.One2many(
        "medical.product.product", inverse_name="product_tmpl_id"
    )

    product_count = fields.Integer(compute="_compute_product_count")

    product_type = fields.Selection(
        selection=[("device", "Device"), ("medication", "Medication")],
        default="medication",
    )

    code_template = fields.Char()
    # Fhir Concept: Code

    ingredients = fields.Text()

    dosage = fields.Char()

    form_id = fields.Many2one(comodel_name="medication.form")
    # Fhir Concept: Form

    form_name = fields.Char(related="form_id.name", string="Form Name")

    administration_route_ids = fields.Many2many("medical.administration.route")

    @api.depends("product_ids")
    def _compute_product_count(self):
        for rec in self:
            rec.product_count = len(rec.product_ids)

    def _get_name_fields(self):
        return ["name", "dosage", "form_name"]

    @api.depends(_get_name_fields)
    def _compute_medical_product_name(self):
        for rec in self:
            name = ""
            for field in rec._get_name_fields():
                if hasattr(rec, field) and getattr(rec, field):
                    name += "%s " % getattr(rec, field)
            rec.name_template = name

    def action_view_medical_product_ids(self):
        action = self.env.ref(
            "medical_product_request.medical_product_product_act_window"
        ).read()[0]
        action["domain"] = [("product_tmpl_id", "=", self.id)]
        if len(self.product_ids) == 1:
            view = "medical_product_request.medical_product_product_form_view"
            action["views"] = [(self.env.ref(view).id, "form")]
            action["res_id"] = self.product_ids.id
        return action


class MedicalProductProduct(models.Model):

    _name = "medical.product.product"
    _description = "Medical Product Product"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _inherits = {"medical.product.template": "product_tmpl_id"}
    _rec_name = "name_product"

    name_product = fields.Char(
        compute="_compute_medical_product_name", store=True
    )
    product_tmpl_id = fields.Many2one(
        "medical.product.template",
        ondelete="cascade",
        copy=True,
        required=True,
    )

    code_product = fields.Char()

    amount = fields.Float(
        help="Amount of drug in package", required=True, default=1
    )
    # Fhir concept: amount

    amount_uom_id = fields.Many2one(comodel_name="uom.uom", required=True)

    amount_uom_name = fields.Char(related="amount_uom_id.name")

    amount_uom_domain = fields.Char(
        compute="_compute_amount_uom_domain", readonly=True, store=False
    )

    def _get_name_fields(self):
        return [
            "name",
            "dosage",
            "form_name",
            "amount",
            "amount_uom_name",
        ]

    @api.depends(_get_name_fields)
    def _compute_medical_product_name(self):
        for rec in self:
            name = ""
            for field in rec._get_name_fields():
                if hasattr(rec, field) and getattr(rec, field):
                    name += "%s " % getattr(rec, field)
            rec.name_product = name

    @api.depends("form_id")
    def _compute_amount_uom_domain(self):
        for rec in self:
            if rec.form_id:
                rec.amount_uom_domain = json.dumps(
                    [("id", "in", rec.form_id.uom_ids.ids)]
                )
            else:
                categ = self.env.ref("uom.product_uom_categ_unit")
                uoms = self.env["uom.uom"].search(
                    [("category_id", "=", categ.id)]
                )
                rec.amount_uom_domain = json.dumps([("id", "in", uoms.ids)])

    # If this is not done, when the product is duplicated, the product template too.
    # We want that the product duplicated has the same template.
    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get("product_tmpl_id", False):
            default["product_tmpl_id"] = self.product_tmpl_id.id
        return super().copy(default=default)

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_("Amount must be positive"))
