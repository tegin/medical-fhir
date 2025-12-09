# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestApp(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url_app = cls.env["medical.imaging.app"].create(
            {
                "name": "Test URL App",
                "app_type": "url",
                "url": "http://example.com/endpoint/{study_uid}",
            }
        )
        cls.study = cls.env["medical.imaging.study"].create(
            {
                "name": "Test Study",
                "instance_uid": "1.2.840.113619.2.55.3.604688123.781.1591781234.467",
            }
        )
        cls.study_2 = cls.env["medical.imaging.study"].create(
            {
                "name": "Test Study 2",
                "instance_uid": "1.2.840.113619.2.55.3.604688123.781.1591781234.468",
            }
        )

    def test_app_info(self):
        app_info = self.study.app_info or []
        app_ids = [app["id"] for app in app_info]
        self.assertIn(self.url_app.id, app_ids)

    def test_app_no_domain(self):
        self.url_app.domain = f"[('instance_uid', '!=', '{self.study.instance_uid}')]"
        app_info = self.study.app_info or []
        app_ids = [app["id"] for app in app_info]
        self.assertNotIn(self.url_app.id, app_ids)
        app_info = self.study_2.app_info or []
        app_ids = [app["id"] for app in app_info]
        self.assertIn(self.url_app.id, app_ids)

    def test_app_ignore_domain(self):
        self.url_app.ignore_domain = (
            f"[('instance_uid', '=', '{self.study.instance_uid}')]"
        )
        app_info = self.study.app_info or []
        app_ids = [app["id"] for app in app_info]
        self.assertNotIn(self.url_app.id, app_ids)
        app_info = self.study_2.app_info or []
        app_ids = [app["id"] for app in app_info]
        self.assertIn(self.url_app.id, app_ids)

    def test_url_app_action(self):
        action = self.study.do_app_action(self.url_app.id)
        self.assertEqual(action["type"], "ir.actions.act_url")
        self.assertEqual(
            action["url"], "http://example.com/endpoint/" + self.study.instance_uid
        )
