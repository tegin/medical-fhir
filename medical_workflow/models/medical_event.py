# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalEvent(models.AbstractModel):
    # FHIR Entity: Event (https://www.hl7.org/fhir/event.html)
    _name = "medical.event"
    _description = "Medical event"
    _inherit = ["medical.abstract", "mail.thread", "mail.activity.mixin"]
    _order = "create_date DESC"

    @api.model
    def _get_states(self):
        return {
            "preparation": ("Preparation", "draft"),
            "in-progress": ("In progress", "draft"),
            "suspended": ("Suspended", "done"),
            "aborted": ("Aborted", "done"),
            "completed": ("Completed", "done"),
            "entered-in-error": ("Entered in error", "done"),
            "unknown": ("Unknown", "done"),
        }

    name = fields.Char(help="Name")
    plan_definition_id = fields.Many2one(
        comodel_name="workflow.plan.definition",
        ondelete="restrict",
        index=True,
        readonly=True,
    )  # FHIR Field: definition

    activity_definition_id = fields.Many2one(
        comodel_name="workflow.activity.definition",
        ondelete="restrict",
        index=True,
        readonly=True,
    )  # FHIR Field: definition

    plan_definition_action_id = fields.Many2one(
        comodel_name="workflow.plan.definition.action",
        index=True,
        readonly=True,
    )  # FHIR Field: definition
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")],
        store=True,
        compute="_compute_state",
    )
    fhir_state = fields.Selection(
        selection=lambda r: [(key, value[0]) for key, value in r._get_states().items()],
        readonly=False,
        required=True,
        tracking=True,
        index=True,
        default="preparation",
    )  # FHIR field: status
    service_id = fields.Many2one(
        string="Service",
        comodel_name="product.product",
        ondelete="restrict",
        index=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        domain="[('type', '=', 'service')]",
    )  # FHIR Field: code
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
    occurrence_date = fields.Datetime(
        string="Occurrence date",
        help="Occurrence of the order.",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )  # FHIR Field: occurrence
    performer_id = fields.Many2one(
        string="Performer",
        comodel_name="res.partner",
        ondelete="restrict",
        index=True,
        tracking=True,
        domain=[("is_practitioner", "=", True)],
        help="Who is to perform the procedure",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )  # FHIR Field : performer/actor

    @api.depends("fhir_state")
    def _compute_state(self):
        state_vals = self._get_states()
        for record in self:
            record.state = state_vals[record.fhir_state][1]

    @api.depends("name", "internal_identifier")
    def name_get(self):
        result = []
        for record in self:
            name = "[%s]" % record.internal_identifier
            if record.name:
                name = "{} {}".format(name, record.name)
            result.append((record.id, name))
        return result

    def preparation2in_progress_values(self):
        return {"fhir_state": "in-progress"}

    def preparation2in_progress(self):
        self.write(self.preparation2in_progress_values())

    def suspended2in_progress_values(self):
        return {"fhir_state": "in-progress"}

    def suspended2in_progress(self):
        self.write(self.suspended2in_progress_values())

    def in_progress2completed_values(self):
        return {"fhir_state": "completed"}

    def in_progress2completed(self):
        self.write(self.in_progress2completed_values())

    def in_progress2aborted_values(self):
        return {"fhir_state": "aborted"}

    def in_progress2aborted(self):
        self.write(self.in_progress2aborted_values())

    def in_progress2suspended_values(self):
        return {"fhir_state": "suspended"}

    def in_progress2suspended(self):
        self.write(self.in_progress2suspended_values())
