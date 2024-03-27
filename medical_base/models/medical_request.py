# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class MedicalRequest(models.AbstractModel):
    # FHIR Entity: Request (https://www.hl7.org/fhir/request.html)
    _name = "medical.request"
    _description = "Medical request"
    _inherit = ["medical.abstract", "mail.thread", "mail.activity.mixin"]
    _order = "create_date DESC"

    @api.model
    def _get_states(self):
        return {
            "draft": ("Draft", "draft"),
            "active": ("Active", "draft"),
            "suspended": ("Suspended", "done"),
            "completed": ("Completed", "done"),
            "entered-in-error": ("Entered in error", "done"),
            "cancelled": ("Cancelled", "done"),
        }

    name = fields.Char(
        help="Name",
        copy=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")],
        store=True,
        compute="_compute_state",
    )
    fhir_state = fields.Selection(
        selection=lambda r: [(key, value[0]) for key, value in r._get_states().items()],
        readonly=True,
        copy=False,
        required=True,
        tracking=True,
        index=True,
        default="draft",
    )  # FHIR field: status
    intent = fields.Selection(
        [
            ("proposal", "Proposal"),
            ("plan", "Plan"),
            ("order", "Order"),
            ("option", "Option"),
        ],
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default="proposal",
    )  # FHIR Field: intent
    priority = fields.Selection(
        [("low", "Low"), ("normal", "Normal"), ("high", "High")],
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        default="normal",
    )  # FHIR Field: priority
    patient_id = fields.Many2one(
        string="Patient",
        comodel_name="medical.patient",
        required=True,
        tracking=True,
        ondelete="restrict",
        index=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Patient Name",
    )  # FHIR field: subject
    performer_id = fields.Many2one(
        string="Performer",
        comodel_name="res.partner",
        domain=[("is_practitioner", "=", True)],
        ondelete="restrict",
        index=True,
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Who is to perform the procedure",
    )  # FHIR Field : performer
    service_id = fields.Many2one(
        string="Service",
        comodel_name="product.product",
        tracking=True,
        ondelete="restrict",
        index=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain="[('type', '=', 'service')]",
    )  # FHIR Field: code
    order_by_id = fields.Many2one(
        string="Ordered by",
        comodel_name="res.partner",
        tracking=True,
        help="Person who has initiated the order.",
        ondelete="restrict",
        index=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )  # FHIR Field: requester/agent
    order_date = fields.Datetime(
        string="Order date",
        help="Start of the order.",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )  # FHIR Field: authoredOn
    observations = fields.Text()  # FHIR Field: note
    is_medical_request = fields.Boolean(
        "Medical request", compute="_compute_is_medical_request"
    )

    @api.depends("fhir_state")
    def _compute_state(self):
        state_vals = self._get_states()
        for record in self:
            record.state = state_vals[record.fhir_state][1]

    def _compute_is_medical_request(self):
        for rec in self:
            rec.is_medical_request = True

    def _get_medical_request_context(self, context):
        for name, field in self._fields.items():
            if (
                field.comodel_name
                and "is_medical_request" in self.env[field.comodel_name]._fields
                and field.type == "many2one"
            ):
                context.update({"default_%s" % field.name: self[name].id})
                if "is_medical_request" in self._fields:
                    if field.comodel_name == self._name:
                        context.update({"default_%s" % field.name: self.id})
                    else:
                        field_id = getattr(self, field.name).id
                        context.update({"default_%s" % field.name: field_id})
        return context

    @api.depends("name", "internal_identifier")
    def name_get(self):
        result = []
        for record in self:
            name = "[%s]" % record.internal_identifier
            if record.name:
                name = "{} {}".format(name, record.name)
            result.append((record.id, name))
        return result

    def draft2active_values(self):
        return {"fhir_state": "active"}

    def draft2active(self):
        self.write(self.draft2active_values())

    def active2suspended_values(self):
        return {"fhir_state": "suspended"}

    def active2suspended(self):
        self.write(self.active2suspended_values())

    def active2completed_values(self):
        return {"fhir_state": "completed"}

    def active2completed(self):
        self.write(self.active2completed_values())

    def active2error_values(self):
        return {"fhir_state": "entered-in-error"}

    def active2error(self):
        self.write(self.active2error_values())

    def reactive_values(self):
        return {"fhir_state": "active"}

    def reactive(self):
        self.write(self.reactive_values())

    def cancel_values(self):
        return {"fhir_state": "cancelled"}

    def cancel(self):
        self.write(self.cancel_values())

    def generate_event(self):
        """Implement method in order to generate an event"""
        raise UserError(_("Function is not defined"))

    @api.model
    def _get_request_models(self):
        return []

    def _get_parents(self):
        return []

    def _check_hierarchy_children(self, vals, counter=1):
        if self._name not in vals:
            vals[self._name] = []
        if self.id in vals[self._name]:
            raise ValidationError(_("Recursion loop found"))
        vals[self._name].append(self.id)
        if counter > 50:
            raise ValidationError(_("Too many recursion"))
        self.ensure_one()
        for model in self._get_request_models():
            for child in self.env[model].search(
                [(self._get_parent_field_name(), "=", self.id)]
            ):
                child._check_hierarchy_children(vals, counter + 1)

    def _get_parent_field_name(self):
        """Implement method in order to return the parent field name"""
        raise UserError(_("Field name is not defined"))

    def action_view_request(self):
        self.ensure_one()
        model = self.env.context.get("model_name", False)
        if model:
            params = self.env[model].action_view_request_parameters()
        else:
            raise UserError(_("No model provided."))
        inverse_name = self._get_parent_field_name()
        requests = self.env[model].search([(inverse_name, "=", self.id)])
        result = self.env["ir.actions.act_window"]._for_xml_id(params["view"])
        context = {"default_patient_id": self.patient_id.id}
        context = self._get_medical_request_context(context)
        result["context"] = context
        result["domain"] = [(inverse_name, "=", self.id)]
        if len(requests) == 1:
            res = self.env.ref(params["view_form"], False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = requests.id
        return result

    @api.constrains("patient_id")
    def _check_patient(self):
        if not self.env.context.get("no_check_patient", False):
            models = self._get_request_models()
            fieldname = self._get_parent_field_name()
            for r in self:
                for model in models:
                    if self.env[model].search(
                        [
                            (fieldname, "=", r.id),
                            ("patient_id", "!=", r.patient_id.id),
                        ],
                        limit=1,
                    ):
                        raise ValidationError(_("Patient must be consistent"))
                for parent in r._get_parents():
                    if parent and parent.patient_id != r.patient_id:
                        raise ValidationError(_("Patient must be consistent"))
