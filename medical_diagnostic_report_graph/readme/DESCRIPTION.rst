This model expands the medical_diagnostic_report by adding the possibility to add a graph and/or an html to the report.

To use it, in a report template mark the fields "Compute Graph" and/or "Compute Html". One page for each case will appear in the template where you can write the desired code.
The html field is done with ir.qweb and the chart can be done using bokeh. You fill find the resources available for the graph at the function "_get_input_dict". In case you needed more resources, just use this function as a hook.

The graphs will appear in the report once validated.

In case you want to hide the observations, you can do it by marking the Hide Observations field.
