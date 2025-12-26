import unittest

from App import create_app
from App.extensions import db
from App.models import Inventory


class InventoryRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            part = Inventory(name="Brake Pad", price=49.99)
            db.session.add(part)
            db.session.commit()
            self.part_id = part.id

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_create_part(self):
        payload = {"name": "Rotor", "price": 89.5}
        resp = self.client.post("/inventory", json=payload)
        self.assertEqual(resp.status_code, 201)

    def test_list_parts(self):
        resp = self.client.get("/inventory")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)

    def test_get_part(self):
        ok = self.client.get(f"/inventory/{self.part_id}")
        self.assertEqual(ok.status_code, 200)
        missing = self.client.get("/inventory/999")
        self.assertEqual(missing.status_code, 404)

    def test_update_part(self):
        resp = self.client.put(f"/inventory/{self.part_id}", json={"price": 55.0})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["price"], 55.0)

    def test_delete_part(self):
        resp = self.client.delete(f"/inventory/{self.part_id}")
        self.assertEqual(resp.status_code, 200)
        missing = self.client.delete(f"/inventory/{self.part_id}")
        self.assertEqual(missing.status_code, 404)


if __name__ == "__main__":
    unittest.main()
