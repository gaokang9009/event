from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class UserDetail(models.Model):
    phone = models.CharField(max_length=14, null=False, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.phone


class Event(models.Model):
    title = models.CharField(max_length=20, null=False, unique=True)
    limit = models.IntegerField(null=False, default=200)
    status = models.IntegerField(choices=((0, '未开始'), (1, '进行中'), (2, '已结束')), default=0)
    address = models.CharField(max_length=255, null=False)
    time = models.DateTimeField(null=False)
    price = models.IntegerField(null=False, default=0)
    type = models.CharField(max_length=20, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Order(models.Model):
    order_code = models.CharField(max_length=18, null=False, unique=True)
    count = models.IntegerField(default=1, null=False)
    ispay = models.IntegerField(choices=((0, '未支付'), (1, '已支付'), (2, '订单异常')), default=0)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.order_code


class Tickets(models.Model):
    ticket_id = models.CharField(max_length=11, null=False, unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return self.ticket_id