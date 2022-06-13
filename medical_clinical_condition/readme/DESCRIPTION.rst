This resource is used to record detailed information about a condition,
problem, diagnosis, or other event, situation, issue, or clinical concept
that has risen to a level of concern.

It can be used to record information about a disease/illness identified from
application of clinical reasoning over the pathologic and pathophysiologic
findings (diagnosis), or identification of health issues/situations that a
practitioner considers harmful, potentially harmful and may be investigated
and managed (problem), or other health issue/situation that may require
ongoing monitoring and/or management (health issue/concern).

The condition resource may be used to record a certain health state of a
patient which does not normally present a negative outcome, e.g. pregnancy.
The condition resource may be used to record a condition following a
procedure, such as the condition of Amputee-BKA following an amputation
procedure.

While conditions are frequently a result of a clinician's assessment and
assertion of a particular aspect of a patient's state of health, conditions
can also be expressed by the patient, related person, or any care team member.
A clinician may have a concern about a patient condition (e.g. anorexia) that
the patient is not concerned about. Likewise, the patient may have a
condition (e.g. hair loss) that does not rise to the level of importance such
that it belongs on a practitioner’s Problem List.

For example, each of the following conditions could rise to the level of
importance such that it belongs on a problem or concern list due to its
direct or indirect impact on the patient’s health:

* Unemployed
* Without transportation (or other barriers)
* Susceptibility to falls
* Exposure to communicable disease
* Family History of cardiovascular disease
* Fear of cancer
* Cardiac pacemaker
* Amputee-BKA
* Risk of Zika virus following travel to a country
* Former smoker
* Travel to a country planned (that warrants immunizations)
* Motor Vehicle Accident
* Patient has had coronary bypass graft

For further information about FHIR Condition visit: https://www.hl7.org/fhir/condition.html


TODO:

* Decide if field medical_condition_ids should contain allergies or not. On one side, allergies are medical.condition records. On the other hand, the information is repeated and can cause confusion as the conditions can be seen from the "Condition" button and the "Allergies" button.
* If finally medical_condition_ids do not contain allergies, the warning_dropdowm from medical_clinical_impression should be modified, as it is computed with the medical_condition_ids.
