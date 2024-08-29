from django.test import SimpleTestCase
from django.urls import reverse


class HealthTest(SimpleTestCase):
    def test_status_code(self):
        """
        Always returns 200OK
        """
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
