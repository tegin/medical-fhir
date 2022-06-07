# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalProductRequestOrder(models.Model):

    _name = "medical.product.request.order"
    _description = "Medical Product Request Order"
    _inherit = ["medical.abstract", "mail.thread", "mail.activity.mixin"]
    _rec_name = "internal_identifier"
    _order = "id desc"

    name = fields.Char()
    internal_identifier = fields.Char(string="Product Request Order")

    category = fields.Selection(
        selection=[("inpatient", "Inpatient"), ("discharge", "Discharge")],
        help="'Inpatient' includes requests for medications to be "
        "administered or consumed in an inpatient or acute care setting "
        " 'Discharge' Includes requests for medications created when "
        "the patient is being released from a facility ",
    )

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

    product_request_ids = fields.One2many(
        comodel_name="medical.product.request",
        inverse_name="request_order_id",
        copy=True,
    )

    patient_id = fields.Many2one(comodel_name="medical.patient", required=True)

    encounter_id = fields.Many2one(
        comodel_name="medical.encounter",
        compute="_compute_last_encounter",
        store=True,
        readonly=False,
    )
    # It is done with a default and not a "compute" because
    # we only want that it is computed when the record is created.

    requester_id = fields.Many2one(
        comodel_name="res.users", readonly=True, copy=False
    )
    validation_date = fields.Datetime(readonly=True, copy=False)
    # Fhir Concept: authoredOn

    cancel_date = fields.Datetime(copy=False)
    cancel_user_id = fields.Many2one(comodel_name="res.users", copy=False)

    can_administrate = fields.Boolean(
        help="Field depending on state used for view and security purposes",
        default=False,
        compute="_compute_can_administrate",
    )
    show_encounter_warning = fields.Boolean(default=False)
    encounter_warning = fields.Char(
        default="This encounter date is more than a week ago. REVISE THE CODE",
        color="red",
        readonly=True,
    )
    medical_product_template_id = fields.Many2one(
        "medical.product.template",
        related="product_request_ids.medical_product_template_id",
        readonly=True,
    )  # used for search purposes

    medical_product_template_ids = fields.Many2many(
        comodel_name="medical.product.template",
        compute="_compute_medical_product_template_ids",
    )
    # This field is used as a fast visualization of products at the order's tree view.

    @api.depends("product_request_ids")
    def _compute_medical_product_template_ids(self):
        for rec in self:
            rec.medical_product_template_ids = rec.product_request_ids.mapped(
                "medical_product_template_id"
            )

    # The _get_last_encounter() function is not used here as in other modules.
    # The reason is that in other modules we want to raise a ValidationError
    # because the encounter is required.
    # But in this case, we can have a medical.product.request without the encounter
    @api.depends("patient_id")
    def _compute_last_encounter(self):
        if self.patient_id and (
            not self.encounter_id
            or self.encounter_id.patient_id != self.patient_id
        ):
            self.encounter_id = self.patient_id._get_last_encounter_or_false()

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code(
                "medical.product.request.order"
            )
            or "/"
        )

    @api.depends("state")
    def _compute_can_administrate(self):
        for rec in self:
            if rec.state == "active":
                rec.can_administrate = True
            else:
                rec.can_administrate = False

    @api.onchange("encounter_id")
    def _onchange_encounter_date(self):
        if self.encounter_id:
            diff = datetime.now() - self.encounter_id.create_date
            if diff >= timedelta(days=7):
                self.show_encounter_warning = True
            else:
                self.show_encounter_warning = False
        else:
            self.show_encounter_warning = False

    def validate_action(self):
        self.ensure_one()
        if not self.product_request_ids:
            raise ValidationError(
                _("It must contain at least one prescription")
            )
        if self.category == "inpatient":
            self.draft2active_action()
        elif self.category == "discharge":
            self.complete_action()

    def _complete_change_state(self):
        return {
            "state": "completed",
            "requester_id": self.env.user.id,
            "validation_date": fields.Datetime.now(),
            "can_administrate": False,
        }

    def complete_action(self):
        self.write(self._complete_change_state())
        self.product_request_ids.complete_action()

    def _draft2active_change_state(self):
        return {
            "state": "active",
            "requester_id": self.env.user.id,
            "validation_date": fields.Datetime.now(),
            "can_administrate": True,
        }

    def draft2active_action(self):
        self.write(self._draft2active_change_state())
        self.product_request_ids.draft2active_action()

    def _cancel_vals(self):
        return {
            "state": "cancelled",
            "cancel_user_id": self.env.user.id,
            "cancel_date": fields.Datetime.now(),
            "can_administrate": False,
        }

    def cancel_action(self):
        self.ensure_one()
        self.write(self._cancel_vals())
        self.product_request_ids.cancel_action()
