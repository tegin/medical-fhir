# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalEncounter(models.Model):
    # FHIR Entity: Encounter (https://www.hl7.org/fhir/encounter.html)
    _name = "medical.encounter"
    _description = "Medical Encounter"
    _inherit = ["medical.abstract", "mail.thread", "mail.activity.mixin"]
    _order = "create_date DESC"

    name = fields.Char(string="Name")
    internal_identifier = fields.Char(string="Encounter")
    patient_id = fields.Many2one(
        string="Patient",
        comodel_name="medical.patient",
        required=True,
        track_visibility=True,
        ondelete="restrict",
        index=True,
        help="Patient name",
    )  # FHIR Field: subject
    priority_id = fields.Selection(
        string="Priority",
        selection=[("UR", "Urgent")],
        help="Indicates the urgency of the encounter.",
    )  # FHIR Field: priority
    location_id = fields.Many2one(
        string="Location",
        comodel_name="res.partner",
        domain=[("is_location", "=", True)],
        track_visibility=True,
        ondelete="restrict",
        index=True,
    )  # FHIR Field: location
    state = fields.Selection(
        string="Encounter Status",
        required="True",
        track_visibility=True,
        selection=[
            ("planned", "Planned"),
            ("arrived", "Arrived"),
            ("in-progress", "In-Progress"),
            ("onleave", "On Leave"),
            ("finished", "Finished"),
            ("cancelled", "Cancelled"),
        ],
        default="arrived",
        help="Current state of the encounter.",
    )  # FHIR Field: status
    is_editable = fields.Boolean(compute="_compute_is_editable")

    @api.model
    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.encounter") or "/"

    @api.depends("name", "internal_identifier")
    def name_get(self):
        result = []
        for record in self:
            name = "[%s]" % record.internal_identifier
            if record.name:
                name = "{} {}".format(name, record.name)
            result.append((record.id, name))
        return result

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in (
                "in-progress",
                "onleave",
                "finished",
                "cancelled",
            ):
                rec.is_editable = False
            else:
                rec.is_editable = True

    def planned2arrived_values(self):
        return {"state": "arrived"}

    def planned2arrived(self):
        self.write(self.planned2arrived_values())

    def planned2cancelled_values(self):
        return {"state": "cancelled"}

    def planned2cancelled(self):
        self.write(self.planned2cancelled_values())

    def arrived2inprogress_values(self):
        return {"state": "in-progress"}

    def arrived2inprogress(self):
        self.write(self.arrived2inprogress_values())

    def arrived2cancelled_values(self):
        return {"state": "cancelled"}

    def arrived2cancelled(self):
        self.write(self.arrived2cancelled_values())

    def inprogress2onleave_values(self):
        return {"state": "onleave"}

    def inprogress2onleave(self):
        self.write(self.inprogress2onleave_values())

    def inprogress2cancelled_values(self):
        return {"state": "cancelled"}

    def inprogress2cancelled(self):
        self.write(self.inprogress2cancelled_values())

    def onleave2finished_values(self):
        return {"state": "finished"}

    def onleave2finished(self):
        self.write(self.onleave2finished_values())

    def onleave2cancelled_values(self):
        return {"state": "cancelled"}

    def onleave2cancelled(self):
        self.write(self.onleave2cancelled_values())
