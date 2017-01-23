from django.test import TestCase

from django.db.models import Q
from django.contrib.auth.models import User

from shop.models import Category, Bonus, Product
from shop.request_user import set_current_user

import datetime

# Create your tests here.


class BonusTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1',
                                              password='qwerty123')
        self.user2 = User.objects.create_user(username='user2',
                                              password='qwerty123')
        self.user3 = User.objects.create_user(username='user3',
                                              password='qwerty123')
        self.user4 = User.objects.create_user(username='user4',
                                              password='qwerty123')

    def check_actual_bonus(self, addition=0):
        for i in range(1, 5):
            user = User.objects.get(username="user%d" % i)
            set_current_user(user)
            try:
                bonus = Bonus.actual.for_current_user.get()
            except Bonus.DoesNotExist:
                bonus = None

            self.assertIsNotNone(bonus)
            self.assertEqual(bonus.percentage, i+addition)

    def test_bonus_creation(self):
        Bonus.objects.create(user=self.user1,
                             start_date=datetime.date(2014, 1, 1),
                             percentage=1)
        Bonus.objects.create(user=self.user2,
                             start_date=datetime.date(2014, 1, 1),
                             percentage=2)
        Bonus.objects.create(user=self.user3,
                             start_date=datetime.date(2014, 1, 1),
                             percentage=3)
        Bonus.objects.create(user=self.user4,
                             start_date=datetime.date(2014, 1, 1),
                             percentage=4)

        self.check_actual_bonus()

        Bonus.objects.create(user=self.user1,
                             percentage=5,
                             start_date=datetime.date(2015, 1, 1))

        Bonus.objects.create(user=self.user2,
                             percentage=6,
                             start_date=datetime.date(2015, 1, 1))

        Bonus.objects.create(user=self.user3,
                             percentage=7,
                             start_date=datetime.date(2015, 1, 1))

        Bonus.objects.create(user=self.user4,
                             percentage=8,
                             start_date=datetime.date(2015, 1, 1))

        self.check_actual_bonus(4)

###
        Bonus.objects.create(user=self.user1,
                             percentage=9)

        Bonus.objects.create(user=self.user2,
                             percentage=10)

        Bonus.objects.create(user=self.user3,
                             percentage=11)

        Bonus.objects.create(user=self.user4,
                             percentage=12)

        self.check_actual_bonus(8)


class ProductTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1',
                                              password='qwerty123')
        self.user2 = User.objects.create_user(username='user2',
                                              password='qwerty123')
        self.user3 = User.objects.create_user(username='user3',
                                              password='qwerty123')
        self.user4 = User.objects.create_user(username='user4',
                                              password='qwerty123')

        Bonus.objects.create(user=self.user1,
                             percentage=9)

        Bonus.objects.create(user=self.user2,
                             percentage=10)

        Bonus.objects.create(user=self.user3,
                             percentage=11)

        self.cat1 = Category.objects.create(name="Категория 1")
        self.cat2 = Category.objects.create(name="Категория 2")
        self.cat3 = Category.objects.create(name="Категория 3")
        self.cat4 = Category.objects.create(name="Категория 4")

        Product.objects.create(category=self.cat1,
                               name="Товар 1-1",
                               description="Описание 1-1",
                               base_price=1100
                               )
        Product.objects.create(category=self.cat1,
                               name="Товар 1-2",
                               description="Описание 1-2",
                               base_price=1200
                               )

        Product.objects.create(category=self.cat2,
                               name="Товар 2-1",
                               description="Описание 2-1",
                               base_price=2100
                               )
        Product.objects.create(category=self.cat2,
                               name="Товар 2-2",
                               description="Описание 2-2",
                               base_price=2200
                               )

    def test_product_price(self):
        set_current_user(self.user1)
        cat1prods = Product.objects.filter(category__name="Категория 1")
        self.assertEqual(cat1prods.count(), 2)

        cat2prods = Product.objects.filter(category__name="Категория 2")
        self.assertEqual(cat2prods.count(), 2)

        set_current_user(self.user1)
        prod11 = cat1prods[0]
        self.assertEqual(prod11.base_price, 1100)
        self.assertEqual(prod11.price, 1001)

        set_current_user(self.user2)
        self.assertEqual(cat1prods[0].price, 990)

        set_current_user(self.user1)
        self.assertEqual(cat2prods[0].price, 1911)

        set_current_user(self.user2)
        self.assertEqual(cat2prods[0].price, 1890)
