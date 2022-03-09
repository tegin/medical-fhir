# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class MedicalPatient(models.Model):

    _inherit = "medical.patient"

    # TODO: add groups to buttons

    external_product_request_order_ids = fields.One2many(
        comodel_name="medical.product.request.order",
        domain=[("state", "!=", "cancelled"), ("category", "=", "discharge")],
        inverse_name="patient_id",
    )

    external_product_request_order_count = fields.Integer(
        compute="_compute_external_medical_product_request_ids"
    )

    internal_product_request_order_ids = fields.One2many(
        comodel_name="medical.product.request.order",
        domain=[("state", "!=", "cancelled"), ("category", "=", "inpatient")],
        inverse_name="patient_id",
    )

    internal_product_request_order_count = fields.Integer(
        compute="_compute_internal_medical_product_request_ids"
    )

    def _get_last_encounter_or_false(self):
        if not self.encounter_ids:
            return False
        return self.encounter_ids[0].id

    def _get_medical_product_request_order_values(self):
        return {
            "encounter_id": self._get_last_encounter_or_false(),
            "patient_id": self.id,
            "category": self.env.context.get("default_category", False),
        }

    def create_medical_product_request(self):
        self.ensure_one()
        view_id = self.env.ref(
            "medical_product_request.medical_product_request_order_form_view"
        ).id
        ctx = dict(self._context)
        vals = self._get_medical_product_request_order_values()
        for key in vals:
            ctx["default_%s" % key] = vals[key]
        ctx["form_view_initial_mode"] = "edit"
        return {
            "type": "ir.actions.act_window",
            "res_model": "medical.product.request.order",
            "name": _("Medical Product Request"),
            "view_type": "form",
            "view_mode": "form",
            "views": [(view_id, "form")],
            "target": "current",
            "context": ctx,
        }

    def _compute_external_medical_product_request_ids(self):
        for rec in self:
            rec.external_product_request_order_count = len(
                rec.external_product_request_order_ids
            )

    def action_view_external_medical_product_request_order_ids(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_product_request.external_medical_product_request_order_act_window"
        ).read()[0]
        if self.external_product_request_order_count == 1:
            view = "medical_product_request.medical_product_request_order_form_view"
            form_view = [(self.env.ref(view).id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view)
                    for state, view in action["views"]
                    if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = self.external_product_request_order_ids.id
        ctx = dict(self._context)
        ctx["default_patient_id"] = self.id
        ctx["default_encounter_id"] = self._get_last_encounter_or_false()
        ctx["default_category"] = "discharge"
        ctx["search_default_not_cancelled"] = 1
        action["context"] = ctx
        action["domain"] = [
            ("patient_id", "=", self.id),
            ("category", "=", "discharge"),
        ]
        return action

    def _compute_internal_medical_product_request_ids(self):
        for rec in self:
            rec.internal_product_request_order_count = len(
                rec.internal_product_request_order_ids
            )

    def action_view_internal_medical_product_request_order_ids(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_product_request.internal_medical_product_request_order_act_window"
        ).read()[0]
        if self.internal_product_request_order_count == 1:
            view = "medical_product_request.medical_product_request_order_form_view"
            form_view = [(self.env.ref(view).id, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view)
                    for state, view in action["views"]
                    if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = self.internal_product_request_order_ids.id
        ctx = dict(self.env.context)
        ctx["default_patient_id"] = self.id
        ctx["default_encounter_id"] = self._get_last_encounter_or_false()
        ctx["default_category"] = "inpatient"
        ctx["search_default_not_cancelled"] = 1
        action["context"] = ctx
        action["domain"] = [
            ("patient_id", "=", self.id),
            ("category", "=", "inpatient"),
        ]
        return action
