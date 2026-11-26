# Copyright 2026 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """The studies of the patient form are shown with sub_view_widget instead of
    the study_ids field. The view of medical_imaging_study_app that extended that
    field would not be valid anymore and would block the update, so it is
    deactivated. It is removed when medical_imaging_study_app is updated."""
    cr.execute(
        """
        UPDATE ir_ui_view SET active = FALSE
        WHERE id IN (
            SELECT res_id FROM ir_model_data
            WHERE module = 'medical_imaging_study_app'
                AND name = 'medical_patient_his_form_view'
                AND model = 'ir.ui.view'
        )
        """
    )
