# Generated by Django 2.2.1 on 2019-05-18 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_deliverytaskstate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliverytaskstate',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
