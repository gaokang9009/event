# Generated by Django 3.0.6 on 2020-06-27 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_tickets'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ispay',
            field=models.IntegerField(choices=[(0, '未支付'), (1, '已支付'), (2, '订单异常')], default=0),
        ),
    ]
