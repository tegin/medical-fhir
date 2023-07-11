# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import math

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_round


class MedicalProductRequest(models.Model):

    _name = "medical.product.request"
    _description = "Medical Product Request"
    _inherit = "medical.abstract"
    _rec_name = "internal_identifier"

    name = fields.Char()

    internal_identifier = fields.Char(string="Product Request")

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("active", "Active"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
    )
    # Fhir Concept: Status

    request_order_id = fields.Many2one(
        comodel_name="medical.product.request.order"
    )

    product_type = fields.Selection(
        related="medical_product_template_id.product_type",
    )

    category = fields.Selection(
        selection=[("inpatient", "Inpatient"), ("discharge", "Discharge")],
        help="'Inpatient' includes requests for medications to be "
        "administered or consumed in an inpatient or acute care setting "
        " 'Discharge' Includes requests for medications created when "
        "the patient is being released from a facility ",
        compute="_compute_category_from_request_order_id",
        store=True,
        readonly=False,
    )
    # Fhir Concept:Category
    # Category, patient_id and encounter_id are done with computes
    # and setting store=True and readonly=False
    # to be able to create medical.product.requests without an order

    validation_date = fields.Datetime(copy=False)
    # Fhir Concept: authoredOn

    medical_product_template_id = fields.Many2one(
        comodel_name="medical.product.template", required=True
    )
    # Fhir Concept: medication

    # Product and quantity to dispense/administrate
    medical_product_id = fields.Many2one(
        comodel_name="medical.product.product",
        compute="_compute_medical_product_id",
        store=True,
    )
    quantity_to_dispense = fields.Integer(
        compute="_compute_medical_product_id",
        store=True,
    )

    patient_id = fields.Many2one(
        comodel_name="medical.patient",
        compute="_compute_patient_id_from_request_order_id",
        store=True,
        readonly=False,
    )
    # Fhir Concept: Subject

    encounter_id = fields.Many2one(
        comodel_name="medical.encounter",
        compute="_compute_encounter_id_from_request_order_id",
        store=True,
        readonly=False,
    )
    # Fhir Concept: Encounter

    requester_id = fields.Many2one(comodel_name="res.users", copy=False)
    # Fhir Concept: Requester

    """Posology FHIR: Dosage"""
    dose_quantity = fields.Float(default=1)
    # Fhir Concept: doseQuantity

    dose_uom_id = fields.Many2one(comodel_name="uom.uom")

    dose_uom_domain = fields.Char(
        compute="_compute_dose_uom_domain", readonly=True, store=False
    )
    rate_quantity = fields.Float(
        compute="_compute_rate_from_specific_rate", store=True
    )
    # Fhir Concept: rateQuantity

    rate_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        compute="_compute_rate_from_specific_rate",
        store=True,
    )

    specific_rate = fields.Float(default=8)

    specific_rate_uom_id = fields.Many2one(
        "uom.uom", default=lambda self: self.env.ref("uom.product_uom_hour").id
    )

    duration = fields.Float(default=7)

    duration_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        default=lambda self: self.env.ref("uom.product_uom_day").id,
    )

    administration_route_id = fields.Many2one(
        comodel_name="medical.administration.route"
    )
    administration_route_domain = fields.Char(
        compute="_compute_administration_route_domain",
        readonly=True,
        store=False,
    )

    product_administration_ids = fields.One2many(
        comodel_name="medical.product.administration",
        inverse_name="product_request_id",
        domain=[("state", "in", ["completed", "cancelled"])],
    )
    product_administrations_count = fields.Integer(
        compute="_compute_product_administrations_count"
    )

    cancel_date = fields.Datetime()
    cancel_user_id = fields.Many2one(comodel_name="res.users", copy=False)

    can_administrate = fields.Boolean(
        help="Field depending on state used for view and security purposes",
        default=False,
    )

    observations = fields.Text()

    @api.depends(
        "request_order_id", "patient_id", "medical_product_template_id"
    )
    def _compute_patient_id_from_request_order_id(self):
        for rec in self:
            if rec.request_order_id:
                rec.patient_id = rec.request_order_id.patient_id.id
            elif self.env.context.get("default_patient_id"):
                rec.patient_id = self.env.context.get("default_patient_id")
            else:
                rec.patient_id = False

    @api.depends(
        "request_order_id",
        "patient_id",
        "encounter_id",
        "medical_product_template_id",
    )
    def _compute_encounter_id_from_request_order_id(self):
        for rec in self:
            if rec.request_order_id:
                rec.encounter_id = rec.request_order_id.encounter_id.id
            elif rec.patient_id:
                rec.encounter_id = (
                    rec.patient_id._get_last_encounter_or_false()
                )
            else:
                rec.encounter_id = False

    # Without the medical_product_template_id dependency it was not computed
    @api.depends(
        "request_order_id", "patient_id", "medical_product_template_id"
    )
    def _compute_category_from_request_order_id(self):
        for rec in self:
            if rec.request_order_id:
                rec.category = rec.request_order_id.category
            elif self.env.context.get("default_category"):
                rec.category = self.env.context.get("default_category")
            else:
                rec.category = False

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.product.request")
            or "/"
        )

    @api.onchange("medical_product_template_id")
    def _get_default_dose_uom_id(self):
        template = self.medical_product_template_id
        if template and template.form_id:
            if template.form_id.uom_ids:
                self.dose_uom_id = template.form_id.uom_ids[0]
        else:
            self.dose_uom_id = self.env.ref("uom.product_uom_unit")

    @api.onchange("medical_product_template_id")
    def _get_default_administration_route_id(self):
        template = self.medical_product_template_id
        if template and template.administration_route_ids:
            self.administration_route_id = template.administration_route_ids[0]
        else:
            self.administration_route_id = False

    @api.depends("medical_product_template_id")
    def _compute_dose_uom_domain(self):
        for rec in self:
            template = rec.medical_product_template_id
            if template and template.form_id:
                rec.dose_uom_domain = json.dumps(
                    [("id", "in", template.form_id.uom_ids.ids)]
                )
            else:
                categ = self.env.ref("uom.product_uom_categ_unit")
                uoms = self.env["uom.uom"].search(
                    [("category_id", "=", categ.id)]
                )
                rec.dose_uom_domain = json.dumps([("id", "in", uoms.ids)])

    @api.depends("medical_product_template_id")
    def _compute_administration_route_domain(self):
        for rec in self:
            template = rec.medical_product_template_id
            if template and template.administration_route_ids:
                rec.administration_route_domain = json.dumps(
                    [("id", "in", template.administration_route_ids.ids)]
                )
            else:
                rec.administration_route_domain = json.dumps([("id", "!=", 0)])

    @api.depends("product_administration_ids")
    def _compute_product_administrations_count(self):
        for rec in self:
            rec.product_administrations_count = len(
                rec.product_administration_ids.filtered(
                    lambda r: r.state == "completed"
                ).ids
            )

    def action_view_medical_product_administration(self):
        action = self.env.ref(
            "medical_product_request.medical_product_administration_act_window"
        ).read()[0]
        action["domain"] = [("product_request_id", "=", self.id)]
        if len(self.product_administration_ids) == 1:
            view = "medical_product_request.medical_product_administration_form_view"
            action["views"] = [(self.env.ref(view).id, "form")]
            action["res_id"] = self.product_administration_ids.id
        return action

    def _get_medical_product_administration_values(self):
        route = (
            self.administration_route_id.id
            if self.administration_route_id
            else False
        )
        return {
            "product_request_id": self.id,
            "medical_product_template_id": self.medical_product_template_id.id,
            "patient_id": self.patient_id.id,
            "encounter_id": self.encounter_id.id
            if self.encounter_id
            else False,
            "quantity_administered": self.dose_quantity or 1,
            "quantity_administered_uom_id": self.dose_uom_id.id,
            "administration_route_id": route,
        }

    def create_medical_product_administration(self):
        self.ensure_one()
        view_id = self.env.ref(
            "medical_product_request.medical_product_administration_pop_up_form_view"
        ).id
        ctx = dict(self._context)
        vals = self._get_medical_product_administration_values()
        for key in vals:
            ctx["default_%s" % key] = vals[key]
        return {
            "type": "ir.actions.act_window",
            "res_model": "medical.product.administration",
            "name": _("Insert administered quantity and validate"),
            "view_type": "form",
            "view_mode": "form",
            "views": [(view_id, "form")],
            "target": "new",
            "context": ctx,
        }

    def _draft2active_change_state(self):
        return {
            "state": "active",
            "requester_id": self.env.user.id,
            "validation_date": fields.Datetime.now(),
            "can_administrate": True,
        }

    def draft2active_action(self):
        for rec in self:
            if rec.state != "active":
                rec.write(self._draft2active_change_state())

    def _complete_change_state(self):
        return {
            "state": "completed",
            "requester_id": self.env.user.id,
            "validation_date": fields.Datetime.now(),
            "can_administrate": False,
        }

    def complete_action(self):
        for rec in self:
            if rec.state != "completed":
                rec.write(rec._complete_change_state())

    def validate_action(self):
        self.ensure_one()
        if self.category == "inpatient":
            self.draft2active_action()
        elif self.category == "discharge":
            self.complete_action()

    def _cancel_vals(self):
        return {
            "state": "cancelled",
            "cancel_user_id": self.env.user.id,
            "cancel_date": fields.Datetime.now(),
            "can_administrate": False,
        }

    def _check_if_cancellable(self):
        if self.product_administrations_count:
            return False
        return True

    def cancel_action(self):
        for rec in self:
            if rec._check_if_cancellable():
                rec.write(rec._cancel_vals())
            else:
                raise ValidationError(
                    _(
                        "You cant not cancel a medical product request "
                        "that has administrations completed"
                    )
                )

    @api.constrains("dose_quantity")
    def _check_dose_quantity(self):
        for rec in self:
            if rec.dose_quantity < 1:
                raise ValidationError(_("Dose must be positive"))

    @api.constrains("rate_quantity")
    def _check_rate_quantity(self):
        for rec in self:
            if rec.product_type == "medication" and rec.rate_quantity <= 0:
                raise ValidationError(_("Rate must be positive"))

    @api.constrains("specific_rate")
    def _check_specific_rate_quantity(self):
        for rec in self:
            if rec.product_type == "medication" and rec.specific_rate <= 0:
                raise ValidationError(_("Rate must be positive"))

    @api.constrains("duration")
    def _check_duration(self):
        for rec in self:
            if rec.product_type == "medication" and rec.duration < 1:
                raise ValidationError(_("Duration must be positive"))

    # This is done just for security to avoid infinite loops.
    # For example, if the amount of a product was 0
    def _get_loop_security_limit(self):
        return 50

    def _get_amount_in_dose_uom_id(self, product):
        return product.amount_uom_id._compute_quantity(
            product.amount, self.dose_uom_id
        )

    def _get_total_dose(self):
        duration_in_rate_uom_id = self.duration_uom_id._compute_quantity(
            self.duration, self.rate_uom_id
        )
        return (
            self.dose_quantity * self.rate_quantity * duration_in_rate_uom_id
        )

    def _select_product_and_quantity(self, template):
        self._get_loop_security_limit()
        total_dose = self._get_total_dose()
        product_info = []
        for product in template.product_ids.filtered(
            lambda r: self._filter_product(r)
        ):
            amount = self._get_amount_in_dose_uom_id(product)
            to_dispense = math.ceil(total_dose / amount)
            product_info.append(
                (product.id, to_dispense, to_dispense * amount - total_dose)
            )
        product_id, to_dispense, remain_dose = sorted(
            product_info, key=lambda value: (value[2], value[1])
        )[0]
        return product_id, to_dispense

    def _filter_product(self, product):
        return True

    @api.depends(
        "medical_product_template_id",
        "dose_quantity",
        "dose_uom_id",
        "rate_quantity",
        "rate_uom_id",
        "duration",
        "duration_uom_id",
    )
    def _compute_medical_product_id(self):
        for rec in self:
            template = rec.medical_product_template_id
            product_id = False
            qty = 0
            if (
                rec.category == "discharge"
                and template
                and template.product_ids
            ):
                if template.product_type == "medication":
                    # Search the most appropriate medical_product_id
                    # and quantity to dispense
                    product_id, qty = rec._select_product_and_quantity(
                        template
                    )
                else:
                    product_id = template.product_ids[0].id
                    qty = rec.dose_quantity
            rec.medical_product_id = product_id
            rec.quantity_to_dispense = qty

    # This computation will have sense once we do the electronic prescription.
    # We will have to think about what happens when we have decimals.
    # For example, every 72 hours, which gives 2'33...
    # Now is it rounded until the most proximal 0.5 up. In this case it would be 2.5.
    @api.depends("specific_rate", "specific_rate_uom_id")
    def _compute_rate_from_specific_rate(self):
        for rec in self:
            if rec.specific_rate_uom_id == self.env.ref(
                "uom.product_uom_hour"
            ):
                if rec.specific_rate <= 24:
                    rate = 24 / rec.specific_rate
                    rate_uom_id = self.env.ref("uom.product_uom_day").id
                else:
                    rate = 24 * 7 / rec.specific_rate
                    rate_uom_id = self.env.ref(
                        "medical_product_request.product_uom_week"
                    ).id
            elif rec.specific_rate_uom_id == self.env.ref(
                "uom.product_uom_day"
            ):
                rate = 1 / rec.specific_rate
                rate_uom_id = rec.specific_rate_uom_id.id
            else:  # specific_rate_uom_id == week
                rate = 1 / rec.specific_rate
                rate_uom_id = rec.specific_rate_uom_id.id
            rate_rounded = 0.5 * float_round(
                rate / 0.5, precision_digits=0, rounding_method="UP"
            )
            rec.rate_quantity = rate_rounded
            rec.rate_uom_id = rate_uom_id
