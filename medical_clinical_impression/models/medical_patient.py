# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MedicalPatient(models.Model):

    _inherit = "medical.patient"

    medical_impression_ids = fields.One2many(
        "medical.clinical.impression",
        inverse_name="patient_id",
    )
    impression_specialty_ids = fields.One2many(
        "medical.specialty", compute="_compute_impression_specialties"
    )

    family_history_ids = fields.One2many(
        "medical.family.member.history", inverse_name="patient_id"
    )

    family_history_count = fields.Integer(
        compute="_compute_family_history_count"
    )

    @api.depends("family_history_ids")
    def _compute_family_history_count(self):
        self.family_history_count = len(self.family_history_ids)

    @api.depends("medical_impression_ids")
    def _compute_impression_specialties(self):
        for record in self:
            record.impression_specialty_ids = (
                record.medical_impression_ids.mapped("specialty_id")
            )

    def action_view_clinical_impressions(self):
        self.ensure_one()
        encounter = self._get_last_encounter()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_clinical_impression."
            "medical_clinical_impression_act_window"
        )
        action["domain"] = [("patient_id", "=", self.id)]
        if encounter:
            action["context"] = {
                "default_encounter_id": encounter.id,
                "search_default_filter_not_cancelled": True,
            }
        return action

    def action_view_family_history_tree(self):
        self.ensure_one()
        view_id = self.env.ref(
            "medical_clinical_impression.medical_family_member_history_view_tree"
        ).id
        ctx = dict(self._context)
        ctx["default_patient_id"] = self.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "medical.family.member.history",
            "name": _("Create family member history 2"),
            "view_type": "list,form",
            "view_mode": "tree",
            "views": [(view_id, "list"), (False, "form")],
            "context": ctx,
            "domain": [("patient_id", "=", self.id)],
        }

    def action_view_medical_procedure_tree(self):
        self.ensure_one()
        view_id = self.env.ref(
            "medical_clinical_procedure.medical_procedure_view_tree"
        ).id
        ctx = dict(self._context)
        ctx["default_patient_id"] = self.id

        return {
            "type": "ir.actions.act_window",
            "res_model": "medical.procedure",
            "name": "Medical Procedures",
            "view_type": "list",
            "view_mode": "tree",
            "views": [(view_id, "list")],
            "context": ctx,
            "domain": [("patient_id", "=", self.id)],
        }

    def action_view_family_history(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_clinical_impression."
            "medical_family_member_history_action"
        )
        action["domain"] = [
            ("patient_id", "=", self.id),
        ]

        action["context"] = {"default_patient_id": self.id}
        return action

    def create_family_member_history(self):
        self.ensure_one()
        view_id = self.env.ref(
            "medical_clinical_impression.medical_family_member_history_view_form"
        ).id
        ctx = dict(self._context)
        ctx["default_patient_id"] = self.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "medical.family.member.history",
            "name": _("Create family member history"),
            "view_type": "form",
            "view_mode": "form",
            "views": [(view_id, "form")],
            "target": "new",
            "context": ctx,
        }

    def get_patient_data(self):
        condition_names = []
        allergy_names = []
        for i in self.medical_condition_ids:
            if i.is_allergy:
                allergy_names.append(
                    "%s (%s)" % (i.name, i.create_date.date())
                )
            else:
                condition_names.append(
                    "%s (%s)" % (i.name, i.create_date.date())
                )
        gender = False
        if self.gender:
            for item in self._fields["gender"]._description_selection(
                self.env
            ):
                if item[0] == self.gender:
                    gender = item[1]
                    continue
        return {
            "name": self.name,
            "condition_count": self.medical_condition_count,
            "condition_names": condition_names,
            "allergy_names": allergy_names,
            "gender": gender,
            "patient_age": self.patient_age,
        }

    def create_impression(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        ctx.update({"impression_view": True, "default_patient_id": self.id})
        if ctx.get("default_specialty_id"):
            self.env["create.impression.from.patient"].with_context(
                **ctx
            ).create({}).generate()
            return {"type": "ir.actions.act_view_reload"}
        xmlid = "medical_clinical_impression.create_impression_from_patient_act_window"
        action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)
        action["context"] = ctx
        return action
