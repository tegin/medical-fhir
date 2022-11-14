# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import io

import numpy as np
import pandas as pd
from bokeh import (
    embed as bokeh_embed,
    layouts as bokeh_layouts,
    models as bokeh_models,
    themes as bokeh_themes,
)
from bokeh.embed.util import FromCurdoc
from bokeh.plotting import figure
from lxml import etree

from odoo import fields, models
from odoo.tools.safe_eval import safe_eval, wrap_module

# from bokeh.io.export import get_screenshot_as_png
from .export_png import get_screenshot_as_png


class MedicalDiagnosticReport(models.Model):

    _inherit = "medical.diagnostic.report"

    bokeh_chart = fields.Text(copy=False)
    html_chart = fields.Html()
    bokeh_image = fields.Binary(copy=False)

    def _get_np_list(self):
        return ["nan"]

    def _get_bokeh_models_list(self):
        return ["ColumnDataSource", "Range1d", "Legend", "LegendItem"]

    def _get_bokeh_widgets_list(self):
        return ["nan"]

    def _get_input_dict(self):
        wrapped_pd = wrap_module(pd, ["DataFrame"])
        wrapped_np = wrap_module(np, self._get_np_list())
        return {
            "observations": self.observation_ids,
            "pd": wrapped_pd,
            "np": wrapped_np,
            "figure": figure,
            "bokeh_embed": wrap_module(bokeh_embed, bokeh_embed.__all__),
            "bokeh_layouts": wrap_module(bokeh_layouts, bokeh_layouts.__all__),
            "bokeh_annotations": wrap_module(
                bokeh_models.annotations, bokeh_models.annotations.__all__
            ),
            # "bokeh_widgets": wrap_module(bokeh_widgets, self._get_bokeh_widgets_list()),
            "bokeh_models": wrap_module(
                bokeh_models, self._get_bokeh_models_list()
            ),
            "bokeh_themes": wrap_module(bokeh_themes, bokeh_themes.__all__),
            "self": self,
        }

    def _compute_report_chart(self):
        if self.compute_graph:
            bokeh = self._get_bokeh_information()
            self.bokeh_chart = bokeh
        if self.compute_html:
            html = self._get_html_information()
            self.html_chart = html

    def _get_html_information(self):
        for template in self.template_ids:
            if not template.compute_html:
                continue
            code = template.html_code
            tree = etree.fromstring(code)
            html = self.env["ir.qweb"]._render(
                tree,
                {"record": self},
            )
            return html
        return False

    def _get_bokeh_information(self, final=False):
        bokeh = False
        for template in self.template_ids:
            if not template.compute_graph:
                continue
            code = template.graph_python_code
            results = self._get_input_dict()
            safe_eval(code or "", results, mode="exec", nocopy=True)
            data = results.get("result", {})
            if "result_data" in data and not final:
                script, div = bokeh_embed.components(
                    data["result_data"],
                    theme=data.get("result_theme", FromCurdoc),
                )
                bokeh = "{}{}".format(div, script)
            elif "result_data" in data:
                img = get_screenshot_as_png(
                    data["result_data"],
                    theme=data.get("result_theme", FromCurdoc),
                )
                output = io.BytesIO()
                img.save(output, format="PNG")
                bokeh = base64.b64encode(output.getvalue())
                output.close()
            return bokeh
        return False

    def _get_image_from_code(self):
        if self.compute_graph:
            bokeh_image = self._get_bokeh_information(True)
            self.bokeh_image = bokeh_image
        if self.compute_html:
            html_chart = self._get_html_information()
            self.html_chart = html_chart

    def registered2final_action(self):
        self._get_image_from_code()
        super().registered2final_action()

    def show_graphs(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        self.flush()
        self._compute_report_chart()
        return {
            "type": "ir.actions.act_window",
            "name": self.display_name,
            "res_model": self._name,
            "res_id": self.id,
            "target": "current",
            "view_mode": "form",
            "context": ctx,
            "views": [
                (
                    self.env.ref(
                        "medical_diagnostic_report_graph."
                        "medical_diagnostic_report_form_view_preview_graph"
                    ).id,
                    "form",
                )
            ],
        }
