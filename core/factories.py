import factory
from faker import Factory
from faker.providers.python import Provider
from django.contrib.auth.hashers import make_password

from .models import Account, User

fake = Factory.create()
fake.seed(1)
provider = Provider(fake)


class SuperUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Faker('email')
    password = factory.LazyFunction(lambda: make_password('pi3.1415'))
    is_staff = True
    is_superuser = True


class AccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = Account

    user = factory.SubFactory(SuperUserFactory)
    money = provider.pydecimal()
