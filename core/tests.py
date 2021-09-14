from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from core.models import Account


class UserTestCase(APITestCase):

    def setUp(self):
        # set up user 1
        u1 = User(
            username="dummy1",
            first_name="dummy",
            last_name="user"
        )
        u1.save()
        Account(
            user=u1,
            inn="1",
            account=10000.0
        ).save()
        self.user = u1

        # set up user 2
        u2 = User(
            username="dummy2",
            first_name="dummy",
            last_name="user"
        )
        u2.save()
        Account(
            user=u2,
            inn="2",
            account=0.0
        ).save()

        # set up user 3
        u3 = User(
            username="dummy3",
            first_name="dummy",
            last_name="user"
        )
        u3.save()
        Account(
            user=u3,
            inn="3",
            account=0.0
        ).save()

    def assertNoChangesCommitted(self, client):
        response = client.get("/api/users/1/", format="json")
        self.assertEqual(response.data["account"], 10000.0)

        response = client.get("/api/users/2/", format="json")
        self.assertEqual(response.data["account"], 0.0)

        response = client.get("/api/users/3/", format="json")
        self.assertEqual(response.data["account"], 0.0)

    def test_retrieve(self):
        self.client.force_login(user=self.user)
        response = self.client.get("/api/users/1/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "dummy1")
        self.assertEqual(response.data["first_name"], "dummy")
        self.assertEqual(response.data["last_name"], "user")
        self.assertEqual(response.data["inn"], "1")
        self.assertEqual(response.data["account"], 10000.0)

    def test_list(self):
        self.client.force_login(user=self.user)
        response = self.client.get("/api/users/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        u1 = response.data[0]
        self.assertEqual(u1["username"], "dummy1")
        self.assertEqual(u1["first_name"], "dummy")
        self.assertEqual(u1["last_name"], "user")
        self.assertEqual(u1["inn"], "1")
        self.assertEqual(u1["account"], 10000.0)

    def test_create(self):
        self.client.force_login(user=self.user)
        response = self.client.post(
            "/api/users/",
            data={
                "username": "test",
                "first_name": "test",
                "last_name": "test",
                "inn": "test",
                "account": 0.0
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "test")
        self.assertEqual(response.data["first_name"], "test")
        self.assertEqual(response.data["last_name"], "test")
        self.assertEqual(response.data["inn"], "test")
        self.assertEqual(response.data["account"], 0.0)

    def test_update(self):
        self.client.force_login(user=self.user)
        response = self.client.put(
            "/api/users/1/",
            data={
                "username": "test",
                "first_name": "test",
                "last_name": "test",
                "inn": "test",
                "account": 0.0
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "test")
        self.assertEqual(response.data["first_name"], "test")
        self.assertEqual(response.data["last_name"], "test")
        self.assertEqual(response.data["inn"], "test")
        self.assertEqual(response.data["account"], 0.0)

    def test_transfer(self):
        """
        Transfer 10000 from user1 to user2 and user3.
        By the end user1 has 0, user2 has 5000 and user3 has 5000
        """
        self.client.force_login(user=self.user)
        response = self.client.post(
            "/api/users/1/transfer/",
            data={"to": ["2", "3"], "amount": 10000.0},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get("/api/users/1/", format="json")
        self.assertEqual(response.data["account"], 0.0)

        response = self.client.get("/api/users/2/", format="json")
        self.assertEqual(response.data["account"], 5000.0)

        response = self.client.get("/api/users/3/", format="json")
        self.assertEqual(response.data["account"], 5000.0)

    def test_transfer_empty_to(self):
        """param to is an empty list"""
        self.client.force_login(user=self.user)
        response = self.client.post(
            "/api/users/1/transfer/",
            data={"to": [], "amount": 0.0},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertNoChangesCommitted(self.client)

    def test_transfer_repeating_to(self):
        """No repeating is allowed"""

        self.client.force_login(user=self.user)
        response = self.client.post(
            "/api/users/1/transfer/",
            data={"to": ["2", "2"], "amount": 0.0},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertNoChangesCommitted(self.client)

    def test_transfer_negative_amount(self):
        """Amount is non negative"""
        self.client.force_login(user=self.user)
        response = self.client.post(
            "/api/users/1/transfer/",
            data={"to": [], "amount": -1},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertNoChangesCommitted(self.client)

    def test_transfer_amount_is_not_enough(self):
        """User's money are not enough """
        self.client.force_login(user=self.user)
        response = self.client.post(
            "/api/users/1/transfer/",
            data={"to": ["2", "3"], "amount": 10e5},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertNoChangesCommitted(self.client)

    def test_transfer_some_inn_missing(self):
        """Some inn provided doesn't exist"""
        self.client.force_login(user=self.user)
        response = self.client.post(
            "/api/users/1/transfer/",
            data={"to": ["2", "non-existing inn"], "amount": 10000.0},
            format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertNoChangesCommitted(self.client)
