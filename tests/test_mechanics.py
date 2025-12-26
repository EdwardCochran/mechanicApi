import unittest

from App import create_app
from App.extensions import db
from App.models import Mechanic


class MechanicRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            seed = Mechanic(
                name="Seed Mech",
                email="seedmech@example.com",
                phone="9998887777",
                password="seedpass",
                salary=50000,
            )
            db.session.add(seed)
            db.session.commit()
            self.seed_id = seed.id

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_create_mechanic(self):
        payload = {
            "name": "Bob Wrench",
            "email": "bob@example.com",
            "phone": "1234567890",
            "password": "pass",
            "salary": 55000,
        }
        resp = self.client.post("/mechanics", json=payload)
        self.assertEqual(resp.status_code, 201)

    def test_create_mechanic_bad_phone(self):
        payload = {
            "name": "Bad Phone",
            "email": "bad@example.com",
            "phone": "12345",
            "password": "pass",
            "salary": 40000,
        }
        resp = self.client.post("/mechanics", json=payload)
        self.assertEqual(resp.status_code, 400)

    def test_get_mechanics(self):
        resp = self.client.get("/mechanics")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)

    def test_get_mechanic_by_id_and_not_found(self):
        ok = self.client.get(f"/mechanics/{self.seed_id}")
        self.assertEqual(ok.status_code, 200)
        missing = self.client.get("/mechanics/999")
        self.assertEqual(missing.status_code, 404)

    def test_update_mechanic(self):
        payload = {"name": "Updated", "phone": "1234567890"}
        resp = self.client.put(f"/mechanics/{self.seed_id}", json=payload)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["name"], "Updated")

    def test_update_mechanic_bad_phone(self):
        payload = {"phone": "12"}
        resp = self.client.put(f"/mechanics/{self.seed_id}", json=payload)
        self.assertEqual(resp.status_code, 400)

    def test_delete_mechanic(self):
        resp = self.client.delete(f"/mechanics/{self.seed_id}")
        self.assertEqual(resp.status_code, 200)
        missing = self.client.delete(f"/mechanics/{self.seed_id}")
        self.assertEqual(missing.status_code, 404)

    def test_top_by_tickets(self):
        resp = self.client.get("/mechanics/top-by-tickets")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)


if __name__ == "__main__":
    unittest.main()
