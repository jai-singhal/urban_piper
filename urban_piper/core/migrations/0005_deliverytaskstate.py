# Generated by Django 2.2.1 on 2019-05-18 17:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0004_auto_20190518_1140'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryTaskState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('new', 'new'), ('accepted', 'accepted'), ('completed', 'completed'), ('declined', 'declined'), ('cancelled', 'cancelled')], default='new', max_length=12)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('assigned_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.DeliveryTask')),
            ],
            options={
                'verbose_name': 'DeliveryTaskState',
                'verbose_name_plural': 'DeliveryTaskStates',
            },
        ),
    ]
