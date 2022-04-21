This module allows to create clinical impressions from patient and encounter. According to the HL7 standard, a clinical
impression is a record of a a clinical assessment performed to determine what problem(s) may affect the patient.

https://www.hl7.org/fhir/clinicalimpression.html

We use this concept to create part of the clinical history of the patient.

Some of the features of this module are:

* Create clinical impressions from patient and encounter and group them by medical specialities.
* Clinical findings and allergies can be added in these impressions. If those clinical findings have been previously configured to create conditions, when the impression is validated, those findings and allergies will create automatically conditions and allergies for that patient.
* Create the family history of the patient from patient and encounter.
* A report with impression/s can be printed. Private notes can be added to the impression, and those will not be added to the report, ss it represents that are comments that only the doctor/s should see.
* A warning dropdown in patient and impression view has been added, in order to see fast warnings for this patient, like if she is pregnant, or they have a pacemaker...

TODO:

* Security
    * Who should create, view and edit impressions?
    * A doctor can edit a impressions from other doctor?
    * Enable that a impression can only be cancelled by who created it.
