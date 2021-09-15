from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    money = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.user}. {self.money}'


class Transaction(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    from_account = models.ForeignKey(Account, related_name='from_account', on_delete=models.CASCADE)
    to_account = models.ForeignKey(Account, related_name='to_account', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.from_account} - {self.to_account}. {self.amount}. {self.created_at}'

