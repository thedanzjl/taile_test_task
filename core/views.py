from django.db.models import Q
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.settings import api_settings

from .serializers import AccountSerializer, TransactionSerializer
from .models import Account, Transaction


class AccountViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    @action(detail=False, methods=['POST'])
    def transfer(self, request, *args, **kwargs):
        """Сделать перевод с нескольких своих аккаунтов на другой"""
        serializer = TransactionSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['GET'])
    def mine(self, request, *args, **kwargs):
        """Получить только свои аккаунты"""
        queryset = self.get_queryset().filter(user=request.user)
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}


class TransactionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()

    @staticmethod
    def prevent_xss(text):
        return text.replace(')', '').replace('(', '').replace('.', '')

    def get_queryset(self):
        queryset = Transaction.objects.filter(
            Q(from_account__user=self.request.user) | Q(to_account__user=self.request.user)
        )
        created_at_filter = [(k, v) for k, v in self.request.query_params.items() if k.startswith('created_at')]
        if created_at_filter:
            queryset = queryset.filter(**{
                created_at_filter[0][0]: self.prevent_xss(created_at_filter[0][1])
            })

        money_filter = [(k, v) for k, v in self.request.query_params.items() if k.startswith('amount')]
        if money_filter:
            queryset = queryset.filter(**{
                money_filter[0][0]: self.prevent_xss(money_filter[0][1])
            })
        return queryset
