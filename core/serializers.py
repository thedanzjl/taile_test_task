from math import floor
from django.db import transaction
from rest_framework import serializers

from core.models import Account, Transaction


class AccountSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')

    class Meta:
        model = Account
        fields = (
            'id', 'user', 'money'
        )


class TransactionSerializer(serializers.ModelSerializer):
    from_account = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    from_accounts = serializers.PrimaryKeyRelatedField(many=True, write_only=True,
                                                       queryset=Account.objects.all())
    to_account = serializers.PrimaryKeyRelatedField(many=False,
                                                    queryset=Account.objects.all())
    amount = serializers.DecimalField(max_digits=8, decimal_places=2)

    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super().__init__(many=many, *args, **kwargs)

    class Meta:
        model = Transaction
        fields = (
            'id', 'created_at', 'from_account', 'to_account', "from_accounts", "amount"
        )

    def validate_from_accounts(self, value):
        user = self.context.get("user")
        if not all([account.user == user for account in value]):
            raise serializers.ValidationError(
                f'You can not transfer money from other accounts')
        return value

    def validate_amount(self, value):
        if value < 0.0:
            raise serializers.ValidationError("The amount should be non negative")
        return value

    @transaction.atomic
    def create(self, validated_data):
        senders = validated_data["from_accounts"]
        recipient = validated_data["to_account"]
        transfer_amount = validated_data["amount"]

        # divide transfer amount among recipients with associated accounts
        transfer_amount_each = floor(transfer_amount / len(senders))

        # transfer money from senders
        for sender in senders:
            if sender.money < transfer_amount_each:
                raise serializers.ValidationError(f'Account {sender.id} has not enough money ({sender.money})')
            sender.money -= transfer_amount_each
            sender.save()

        recipient.money += transfer_amount_each * len(senders)
        recipient.save()

        transactions = Transaction.objects.bulk_create([
            Transaction(from_account=sender, to_account=recipient, amount=transfer_amount_each)
            for sender in senders
        ])

        return transactions
