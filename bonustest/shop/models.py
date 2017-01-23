from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import formats
from django.utils.translation import ugettext_lazy as _

import datetime

from .request_user import (
    get_current_user, get_user_bonus, set_user_bonus,
    current_user_changed_signal
)

# Create your models here.


class ActualBonusManager(models.Manager):
    def get_queryset(self):
        today = datetime.date.today()
        return super(ActualBonusManager, self) \
            .get_queryset() \
            .filter(start_date__lte=today) \
            .filter(Q(end_date__gte=today) |
                    Q(end_date__isnull=True))

    def for_user(self, user):
        qs = self.get_queryset()
        if user.is_authenticated:
            return qs.filter(user=user)
        else:
            return qs.filter(user=None)

    @property
    def for_current_user(self):
        return self.for_user(get_current_user())


class Category(models.Model):
    name = models.CharField(max_length=20,
                            verbose_name=_("category name"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")


class Bonus(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name=_("user"))
    start_date = models.DateField(verbose_name=_("start date"))
    end_date = models.DateField(blank=True,
                                null=True,
                                verbose_name=_("end date"))
    percentage = models.IntegerField(default=0,
                                     verbose_name=_("percentage"))
    objects = models.Manager()
    actual = ActualBonusManager()

    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.start_date is None:
                self.start_date = datetime.date.today()
            try:
                current_bonus = Bonus.actual.for_user(self.user).get()
            except Bonus.DoesNotExist:
                current_bonus = None
            if not(current_bonus is None):
                current_bonus.end_date = self.start_date \
                                        - datetime.timedelta(days=1)
                current_bonus.save()
        super(Bonus, self).save(*args, **kwargs)

    def __str__(self):
        return _("%(percentage)d%% for %(user)s from "
                 "%(start_date)s to %(end_date)s") % \
                 {
                    "percentage": self.percentage,
                    "user": self.user.username,
                    "start_date": formats.date_format(self.start_date,
                                                      "SHORT_DATE_FORMAT"),
                    "end_date": "ever" if self.end_date is None
                                else formats.date_format(self.end_date,
                                                         "SHORT_DATE_FORMAT"),
                }

    class Meta:
        verbose_name = _("bonus")
        verbose_name_plural = _("bonuses")


class Product(models.Model):
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 blank=True,
                                 null=True,
                                 verbose_name=_("category"))
    name = models.CharField(max_length=50,
                            verbose_name=_("name"))
    description = models.CharField(max_length=500,
                                   blank=True,
                                   null=True,
                                   verbose_name=_("description"))
    base_price = models.DecimalField(decimal_places=2,
                                     max_digits=10,
                                     verbose_name=_("base price"))

    def __init__(self, *args, **kwargs):
        super(__class__, self).__init__(*args, **kwargs)
        self.user_changed(None, None)
        current_user_changed_signal.connect(self.user_changed)

    def user_changed(self, sender, signal, **kwargs):
        try:
            bonus = Bonus.actual.for_current_user.get()
            bonus_value = bonus.percentage
        except Bonus.DoesNotExist:
            bonus_value = 0
        set_user_bonus(bonus_value)
        self.bonus = bonus_value

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")

    @property
    def price(self):
        real_price = float(self.base_price)
        real_price -= round(real_price*self.bonus/100, 2)
        return real_price
