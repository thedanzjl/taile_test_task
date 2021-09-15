from rest_framework.test import APIRequestFactory, APITestCase
from http import HTTPStatus

from core.models import Transaction
from .factories import AccountFactory, SuperUserFactory

api_factory = APIRequestFactory()


class AccountTestCase(APITestCase):

    def setUp(self):
        self.user1 = SuperUserFactory(username='user1')
        self.user2 = SuperUserFactory(username='user2')
        self.acc11 = AccountFactory(user=self.user1, money=1000)
        self.acc12 = AccountFactory(user=self.user1, money=1000)
        self.acc21 = AccountFactory(user=self.user2, money=1000)
        self.acc22 = AccountFactory(user=self.user2, money=1000)

    def test_accounts_list(self):
        self.client.force_login(user=self.user1)
        resp = self.client.get('/accounts/', format='json')
        self.assertEqual(len(resp.data['results']), 4)  # 2 accounts

    def test_accounts_get(self):
        self.client.force_login(user=self.user1)
        resp = self.client.get(f'/accounts/{self.acc11.id}/', format='json')
        self.assertEqual(float(resp.data['money']), 1000.0)

    def test_transfer_okay(self):
        self.client.force_login(user=self.user1)
        self.client.post('/accounts/transfer/', format='json', data={
            'from_accounts': [self.acc11.id, self.acc12.id],
            'to_account': self.acc21.id,
            'amount': 1000
        })
        self.assertEqual(len(Transaction.objects.all()), 2)
        self.assertEqual(Transaction.objects.get(from_account=self.acc11).amount, 500)
        self.assertEqual(Transaction.objects.get(from_account=self.acc12).amount, 500)

    def test_transfer_low_money(self):
        self.client.force_login(user=self.user1)
        resp = self.client.post('/accounts/transfer/', format='json', data={
            'from_accounts': [self.acc11.id, self.acc12.id],
            'to_account': self.acc21.id,
            'amount': 10000
        })
        self.assertEqual(resp.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(len(Transaction.objects.all()), 0)

    def test_transfer_from_strangers_account(self):
        self.client.force_login(user=self.user2)  # logged in as user2 trying to transfer money from user1
        resp = self.client.post('/accounts/transfer/', format='json', data={
            'from_accounts': [self.acc11.id, self.acc12.id],
            'to_account': self.acc21.id,
            'amount': 1000
        })
        self.assertEqual(resp.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(len(Transaction.objects.all()), 0)

    def test_transaction_search(self):
        from datetime import datetime
        now = datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')

        self.test_transfer_okay()
        resp = self.client.get('/transactions/?amount__lte=500', format='json')
        self.assertEqual(resp.data['count'], 2)
        resp = self.client.get('/transactions/?amount__gt=500', format='json')
        self.assertEqual(resp.data['count'], 0)
        resp = self.client.get(f'/transactions/?created_at__gte={now}', format='json')
        self.assertEqual(resp.data['count'], 2)
