import unittest
from datetime import date

from App import create_app
from App.extensions import db
from App.models import Customer, Mechanic, Inventory


class ServiceTicketRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            # seed customer for auth
            cust = Customer(
                name="Ticket Owner",
                email="owner@example.com",
                phone="1012023030",
                password="pass",
            )
            db.session.add(cust)
            # second customer for unauthorized test
            other = Customer(
                name="Other",
                email="other@example.com",
                phone="4045056060",
                password="pass",
            )
            mech = Mechanic(
                name="Mechanic One",
                email="mech1@example.com",
                phone="9998887777",
                password="pass",
                salary=60000,
            )
            part = Inventory(name="Oil Filter", price=9.99)
            db.session.add_all([other, mech, part])
            db.session.commit()
            self.owner_id = cust.id
            self.other_id = other.id
            self.mechanic_id = mech.id
            self.part_id = part.id

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def login(self, email, password):
        resp = self.client.post("/customers/login", json={"email": email, "password": password})
        return resp.get_json().get("auth_token")

    def create_ticket(self, customer_id):
        payload = {
            "vin": "1HGCM82633A004352",
            "service_description": "Brake replacement",
            "service_date": date.today().isoformat(),
            "customer_id": customer_id,
        }
        return self.client.post("/tickets/", json=payload)

    def test_create_ticket_and_list(self):
        resp = self.create_ticket(self.owner_id)
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/tickets/")
        self.assertEqual(list_resp.status_code, 200)
        self.assertIsInstance(list_resp.get_json(), list)

    def test_my_tickets_auth_and_unauth(self):
        token = self.login("owner@example.com", "pass")
        resp = self.client.get("/tickets/my-tickets", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(resp.status_code, 200)
        unauth = self.client.get("/tickets/my-tickets")
        self.assertEqual(unauth.status_code, 401)

    def test_update_and_delete_ticket(self):
        create_resp = self.create_ticket(self.owner_id)
        ticket_id = create_resp.get_json()["id"]
        token = self.login("owner@example.com", "pass")
        update = self.client.put(
            f"/tickets/{ticket_id}",
            json={"service_description": "Updated desc"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(update.status_code, 200)
        delete = self.client.delete(
            f"/tickets/{ticket_id}", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(delete.status_code, 200)
        missing = self.client.delete(
            f"/tickets/{ticket_id}", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(missing.status_code, 404)

    def test_assign_and_remove_mechanic(self):
        create_resp = self.create_ticket(self.owner_id)
        ticket_id = create_resp.get_json()["id"]
        token = self.login("owner@example.com", "pass")
        assign = self.client.put(
            f"/tickets/{ticket_id}/assign-mechanic/{self.mechanic_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(assign.status_code, 200)
        remove = self.client.put(
            f"/tickets/{ticket_id}/remove-mechanic/{self.mechanic_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(remove.status_code, 200)
        # unauthorized with different customer
        other_token = self.login("other@example.com", "pass")
        forbidden = self.client.put(
            f"/tickets/{ticket_id}/assign-mechanic/{self.mechanic_id}",
            headers={"Authorization": f"Bearer {other_token}"},
        )
        self.assertEqual(forbidden.status_code, 403)

    def test_add_part(self):
        create_resp = self.create_ticket(self.owner_id)
        ticket_id = create_resp.get_json()["id"]
        token = self.login("owner@example.com", "pass")
        resp = self.client.put(
            f"/tickets/{ticket_id}/add-part/{self.part_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(resp.status_code, 200)

    def test_edit_mechanics_list(self):
        create_resp = self.create_ticket(self.owner_id)
        ticket_id = create_resp.get_json()["id"]
        resp = self.client.put(
            f"/tickets/{ticket_id}/edit",
            json={"add_ids": [self.mechanic_id]},
        )
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
