# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import numpy as np
import pandas as pd
from bokeh.embed import components
from bokeh.models import BoxAnnotation, ColumnDataSource, DatetimeTickFormatter
from bokeh.models.tools import HoverTool
from bokeh.plotting import figure
from odoo import _, api, fields, models


class PatientConceptEvolution(models.TransientModel):
    _name = "patient.concept.evolution"
    _description = "This wizard allows to view a patient's concept evolution"

    concept_id = fields.Many2one("medical.observation.concept")
    patient_id = fields.Many2one("medical.patient")
    bokeh_chart = fields.Text(compute="_compute_bokeh_chart")
    date_low_limit = fields.Date()
    date_high_limit = fields.Date()

    def _get_dataframe_domain(self):
        domain = [
            ("patient_id", "=", self.patient_id.id),
            ("concept_id", "=", self.concept_id.id),
            ("state", "=", "final"),
        ]
        if self.date_low_limit:
            domain.append(("observation_date", ">=", self.date_low_limit))
        if self.date_high_limit:
            domain.append(("observation_date", "<=", self.date_high_limit))

        return domain

    def _compute_evolution_dataframe(self):
        domain = self._get_dataframe_domain()
        observations = self.env["medical.observation"].search(
            domain, order="observation_date"
        )
        if observations:
            df = pd.DataFrame({"Date": []})
            df = df.set_index("Date")
            for observation in observations:
                obs_date = fields.Datetime.context_timestamp(
                    observation, observation.observation_date
                ).replace(tzinfo=None)
                if observation.name not in df.columns:
                    df[observation.name] = np.nan
                if obs_date not in df.index:
                    df.loc[obs_date] = np.nan
                df.loc[obs_date, observation.name] = observation.get_value()
            return df
        else:
            return False

    @api.depends("concept_id", "date_low_limit", "date_high_limit")
    def _compute_bokeh_chart(self):
        if self.concept_id:
            df = self._compute_evolution_dataframe()
            if not isinstance(df, pd.DataFrame):
                self.bokeh_chart = """
                <div class="alert alert-danger text-center o_form_header"
                     role="alert" style="margin-bottom:0px;"><bold>%s</bold></div>
                """ % _(
                    "No data found"
                )
                return
            source = ColumnDataSource(df)
            p = figure(sizing_mode="stretch_width", plot_height=450,)
            hover = HoverTool(
                tooltips=[
                    ("Date", "@Date{%d/%m/%y}"),
                    (
                        "Value",
                        "@{%s} %s"
                        % (self.concept_id.name, self.concept_id.uom_id.name),
                    ),
                ],
                formatters={"@Date": "datetime"},
                mode="mouse",
            )
            p.add_tools(hover)
            p.toolbar.autohide = True
            p.circle(
                x="Date",
                y="%s" % self.concept_id.name,
                source=source,
                size=6,
                line_color="black",
                fill_color="gray",
            )
            p.line(
                x="Date",
                y="%s" % self.concept_id.name,
                line_color="gray",
                source=source,
                line_width=1,
            )
            p.title.text = "%s" % self.concept_id.name
            p.title.text_font_style = "italic"
            p.title.align = "center"
            p.title.text_font_size = "18px"
            p.xaxis[0].formatter = DatetimeTickFormatter(
                days=["%d/%m/%y"], hours=["%H:%M"]
            )
            p.xgrid[0].grid_line_color = None
            p.ygrid[0].grid_line_alpha = 0.5
            p.xaxis.axis_label = "Date"
            p.yaxis.axis_label = "{} ({})".format(
                self.concept_id.name, self.concept_id.uom_id.name,
            )
            if self.concept_id.reference_range_high:
                if self.concept_id.reference_range_low:
                    low_box = BoxAnnotation(
                        top=self.concept_id.reference_range_low,
                        fill_alpha=0.1,
                        fill_color="red",
                    )
                    mid_box = BoxAnnotation(
                        bottom=self.concept_id.reference_range_low,
                        top=self.concept_id.reference_range_high,
                        fill_alpha=0.1,
                        fill_color="green",
                    )
                    high_box = BoxAnnotation(
                        bottom=self.concept_id.reference_range_high,
                        fill_alpha=0.1,
                        fill_color="red",
                    )
                    p.add_layout(mid_box)
                else:
                    low_box = BoxAnnotation(
                        top=self.concept_id.reference_range_high,
                        fill_alpha=0.1,
                        fill_color="green",
                    )
                    high_box = BoxAnnotation(
                        bottom=self.concept_id.reference_range_high,
                        fill_alpha=0.1,
                        fill_color="red",
                    )
                p.add_layout(low_box)
                p.add_layout(high_box)
            script, div = components(p)
            self.bokeh_chart = "{}{}".format(div, script)
