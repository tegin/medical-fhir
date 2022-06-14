Make sure the user has the permits needed.

Medical Diagnostic Report Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To create a new report template:

#. Go to Clinical -> Report Configuration -> Diagnostic Report Templates
#. Create a new one and configure the report:

    * Report name: the name used to search the report at the report creation wizard
    * Title: name that will appear at the report
    * With observations: When true, the report will have an observations page.
    * Observations: The records added here will appear by default in the report. Each record can be filled with or without a concept . The former it is recommended if you want to keep track of these observations, as for example creating a pivot report or seeing its evolution through time. You can add 4 types of records: line, section, subsection and note. Each of them has a different format. They all can also be blocked, it means that this record will be blocked for the user in the report.
    * Item Blocked: Mark it as true if you want to block all observations records (so only the value field can be edited).
    * With composition: When true, the report will have a composition page.
    * Composition: The html added here will be set as default in the report.
    * With conclusion: When true, the report will have a conclusion page.
    * Conclusion: The text added here will be set as the default conclusion in the report.
    * Report Action: Only visible in debug. If nothing is selected, the template and action are the default ones.
#. You can preview the report with demo data with the "Preview button"

Medical Observation Concept
~~~~~~~~~~~~~~~~~~~~~~~~~~~
To create a new concept:

#. Go to Clinical -> Report Configuration -> Observation Concepts
#. Create a new record.
#. Write the name and the value type. In the case of an integer or float value, write also the unit of measure and, if desired, the reference range. In the case of a selection value, the different options are separated by ";" (Ex: yes;no)

Create a report from an encounter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Select an encounter in Administration -> Encounter and enter in its form view.
#. Click on "Generate Medical Report" and choose the template of the report and the language.
#. Add the desired data.
#. You can add another template by clicking the "Expand" button.
#. Once everything is correct, you can issue the report and print it at "Print -> Diagnostic Report".
#. To ensure that it has not been modified, you can click on the "Signature" button and if the Digest Altered field is false, it means that it has not been modified.

Patient Concept Evolution
~~~~~~~~~~~~~~~~~~~~~~~~~
To see the evolution on a graph of a patient's concept (only for float and integer values):

#. Go to a patient form view and click on "Observations Evolution".
#. Select a concept and filter by dates if desired.
#. You can save the image or perform additional actions.
