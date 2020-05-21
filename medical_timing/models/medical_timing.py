# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from pytz import timezone, UTC
from odoo import fields, models
from datetime import timedelta


class MedicalTiming(models.Model):
    _name = "medical.timing"
    _description = "Medical Timing"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    timing_code = fields.Selection(
        [
            ("QD", "QD"),
            ("AM", "AM"),
            ("PM", "PM"),
            ("BID", "BID"),
            ("TID", "TID"),
            ("QID", "QD"),
        ],
        readonly=True,
        string="FHIR codification",
    )
    timing_period = fields.Integer(string="Period")
    timing_period_unit = fields.Selection(
        [("hours", "Hours"), ("days", "Days"), ("minutes", "Minutes")],
        string="Unit",
    )

    def _closest_next_date_QD(self, local_date, location):
        return self._closest_date_from_list(local_date, [location.timing_qd])

    def _closest_next_date_BID(self, local_date, location):
        return self._closest_date_from_list(
            local_date, [location.timing_bid_1, location.timing_bid_2]
        )

    def _closest_next_date_TID(self, local_date, location):
        return self._closest_date_from_list(
            local_date,
            [
                location.timing_tid_1,
                location.timing_tid_2,
                location.timing_tid_3,
            ],
        )

    def _closest_next_date_QID(self, local_date, location):
        return self._closest_date_from_list(
            local_date,
            [
                location.timing_qid_1,
                location.timing_qid_2,
                location.timing_qid_3,
                location.timing_qid_4,
            ],
        )

    def _closest_next_date_AM(self, local_date, location):
        return self._closest_date_from_list(local_date, [location.timing_am])

    def _closest_next_date_PM(self, local_date, location):
        return self._closest_date_from_list(local_date, [location.timing_pm])

    def _closest_date_from_list(self, local_datetime, hours):
        local_date = local_datetime.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        for hour in hours:
            new_datetime = local_date + timedelta(hours=hour)
            if new_datetime >= local_datetime:
                return new_datetime
        return local_date + timedelta(days=1, hours=hours[0])

    def _next_date_QD(self, current_date, location):
        return current_date + timedelta(days=1)

    def _next_date_AM(self, current_date, location):
        return current_date + timedelta(days=1)

    def _next_date_PM(self, current_date, location):
        return current_date + timedelta(days=1)

    def _next_date_BID(self, current_date, location):
        return current_date + timedelta(hours=12)

    def _next_date_TID(self, current_date, location):
        return current_date + timedelta(hours=8)

    def _next_date_QID(self, current_date, location):
        return current_date + timedelta(hours=6)

    def _closest_next_date(self, current_date=False, location=False):
        if not self:
            return False
        self.ensure_one()
        if not current_date:
            current_date = fields.Datetime.now()
        if not location:
            location = self.env["res.partner"]
        if self.timing_code:
            tz = timezone(location.tz or "UTC")
            if not current_date.tzinfo:
                current_date = current_date.replace(tzinfo=UTC)
            local_date = current_date.astimezone(tz)
            return (
                getattr(self, "_closest_next_date_%s" % self.timing_code)(
                    local_date, location
                )
                .astimezone(UTC)
                .replace(tzinfo=None)
            )
        return current_date

    def _next_date(
        self, current_date=False, location=False, force_closest=False
    ):
        if force_closest:
            return self._closest_next_date(current_date, location)
        if not self:
            return False
        self.ensure_one()
        if not current_date:
            current_date = fields.Datetime.now()
        if self.timing_code:
            return getattr(self, "_next_date_%s" % self.timing_code)(
                current_date=getattr(
                    self, "_closest_next_date_%s" % self.timing_code
                )(current_date=current_date, location=location),
                location=location,
            )
        return current_date + timedelta(
            **{self.timing_period_unit: self.timing_period}
        )
