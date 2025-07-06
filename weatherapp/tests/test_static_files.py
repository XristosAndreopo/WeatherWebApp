# tests/test_static_files.py

import os
from django.test import TestCase
from django.conf import settings

class StaticFilesExistenceTests(TestCase):
    """
    Basic "smoke tests" to ensure key JS/CSS files are present
    (so our front‑end modules at least load).
    """

    def test_theme_js_exists_and_not_empty(self):
        path = os.path.join(settings.BASE_DIR, 'static', 'js', 'theme.js')
        self.assertTrue(os.path.isfile(path), "theme.js must exist")
        self.assertTrue(os.path.getsize(path) > 0, "theme.js must not be empty")

    def test_dashboard_js_exists(self):
        path = os.path.join(settings.BASE_DIR, 'static', 'js', 'dashboard.js')
        self.assertTrue(os.path.isfile(path), "dashboard.js must exist")

    def test_map_js_exists(self):
        path = os.path.join(settings.BASE_DIR, 'static', 'js', 'map.js')
        self.assertTrue(os.path.isfile(path), "map.js must exist")

    def test_find_js_exists(self):
        path = os.path.join(settings.BASE_DIR, 'static', 'js', 'find.js')
        self.assertTrue(os.path.isfile(path), "find.js must exist")
