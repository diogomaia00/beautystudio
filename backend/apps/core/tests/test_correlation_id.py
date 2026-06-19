from django.test import TestCase


class CorrelationIdMiddlewareTests(TestCase):
    def test_generates_request_id_when_absent(self):
        res = self.client.get("/healthz/")
        self.assertIn("X-Request-ID", res)
        self.assertTrue(res["X-Request-ID"])

    def test_echoes_inbound_request_id(self):
        res = self.client.get("/healthz/", HTTP_X_REQUEST_ID="abc-123")
        self.assertEqual(res["X-Request-ID"], "abc-123")
