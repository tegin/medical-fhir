#. Create a clinical finding and mark the field "create_condition_from_clinical_impression" in those which should create conditions automatically from impression.
#. Create an encounter for the patient.
#. Create a new impression:
    * If there are not impressions yet for a speciality, press the button "Create impression", choose a specialty and the encounter. The encounter can be changed and if it is older than a week a warning will appear. Then, click "Create". You can always use this wizard, even if there are already impressions for that specialty.
    * Once there are already impressions of that specialty for a patient, you  can access them from the stethoscope button found on the patient impressions page. Once there, pressing the "Create button" you can create impressions of that specialty.
#. Complete all the desired fields of the impression, also add findings or allergies if desired.
#. When everything is completed, validate the impression. Once validated, it can not be edited. The findings added whose create_condition_from_clinical_impression field was marked as true, will create a condition. The allergies added will also create a allergy.
#. The impression can also be cancelled. The related conditions and allergies created will be desactivated.
#. If desired, create a family history record from the button "Create Family History" at the patient or encounter view.
