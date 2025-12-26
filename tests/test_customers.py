import unittest

from App import create_app
from App.extensions import db


class CustomerRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            # seed a customer for login tests
            from App.models import Customer

            seed = Customer(
                name="Seed User",
                email="seed@example.com",
                phone="1112223333",
                password="seedpass",
            )
            db.session.add(seed)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_get_customers_list(self):
        """GET /customers returns 200 and a paginated list."""
        response = self.client.get("/customers")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        # Paginated format with items key
        self.assertIn("items", data)
        self.assertIsInstance(data["items"], list)

    def test_create_customer(self):
        """POST /customers creates a customer and returns 201."""
        payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "1234567890",
            "password": "123",
        }
        response = self.client.post("/customers", json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "John Doe")

    def test_login_success(self):
        """POST /customers/login with valid credentials returns token."""
        credentials = {
            "email": "seed@example.com",
            "password": "seedpass",
        }
        response = self.client.post("/customers/login", json=credentials)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertIn("auth_token", data)

    def test_login_invalid_credentials(self):
        """POST /customers/login with bad credentials returns 401."""
        credentials = {
            "email": "seed@example.com",
            "password": "wrong",
        }
        response = self.client.post("/customers/login", json=credentials)
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
