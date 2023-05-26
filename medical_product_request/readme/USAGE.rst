First, check that the user has the needed security permits.


Medication Form
~~~~~~~~~~~~~~~

To create a new medication.form:

#. Go to Medical --> Configuration --> Medication Form
#. Create a new record.

The uoms selected on the uom_ids field, will be the ones allowed to choose when creating a medical.product.request of a medication with this form. The first one will be set as default.

Medical Administration Route
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
To create a new medical.administration.route:

#. Go to Medical --> Configuration --> Medical Administration Route
#. Create a new record.

Medical Product
~~~~~~~~~~~~~~~

To create a new medical.product.template there are two options:
    #. Create the medical.product.template record manually:
        * Go to Medical --> Configuration --> Medical Product Template
        * Create a new record and complete the fields. The administration routes selected will be the ones that can be chosen in a request of this product.
        * Go to Medical --> Configuration --> Medical Product
        * Create a new record and select as template the one just created. The fields will be automatically filled.
    #. Create the medical.product.product record, and template created automatically.
        * Go to Medical --> Configuration  --> Medical Product
        * Create a new record and fill all the required fields. DO NOT fill the product_tmpl_id field. When the record is saved, the medical.product.template record is created automatically.

If you want to create a new medical.product.product of an already existing template, just select this template at the product_tmpl_id field.

This amount will be used to compute the quantity to dispense in the case of 'discharge' requests. Set the total quantity of the package. For example, if a package has 5 bottles of 5 ml each, set an amount of 25 ml.

Medical Product Request Order
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A Medical Product Request can be created from an order or not. To create it from a request order the steps are:

External ('discharge') Medical Product Request Order
****************************************************

#. Go to a Patient or an Encounter form and click on "Create Ext. Prescription".
#. Create a new line on prescriptions and set the desired values.
#. Once everything is correct, click "Validate". The state will be set to Completed.

Internal ('inpatient') Medical Product Request Order
****************************************************

#. Go to Patient or an Encounter form and click on "Create Int. Medical Order"
#. Create a new line on prescriptions and set the desired values.
#. Once everything is correct, click "Validate". The state will be set to Active and you'll be able to create administrations.
#. To create an administration for a request click on "Administrate". A pop up will be opened, and the values will be filled by default with the request's values. Change values if needed and validate it.
#. You cannot cancel a request that has completed administrations. To do so, you should cancel them first.
