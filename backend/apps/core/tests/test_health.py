from rest_framework.test import APITestCase


class HealthEndpointTests(APITestCase):
    def test_liveness_returns_ok(self):
        res = self.client.get("/healthz/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ok")

    def test_readiness_reports_database_up(self):
        res = self.client.get("/readyz/")
        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertEqual(body["status"], "ready")
        self.assertTrue(body["database"])

    def test_health_endpoints_need_no_auth(self):
        # No session established — probes must still answer.
        self.assertEqual(self.client.get("/healthz/").status_code, 200)
        self.assertEqual(self.client.get("/readyz/").status_code, 200)
