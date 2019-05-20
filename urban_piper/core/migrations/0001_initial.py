# Generated by Django 2.2.1 on 2019-05-19 09:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryStateTransition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('at', models.DateTimeField(auto_now_add=True)),
                ('by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'DeliveryStateTransition',
                'verbose_name_plural': 'DeliveryStateTransitions',
            },
        ),
        migrations.CreateModel(
            name='DeliveryTaskState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('new', 'new'), ('accepted', 'accepted'), ('completed', 'completed'), ('declined', 'declined'), ('cancelled', 'cancelled')], default='new', max_length=12)),
            ],
            options={
                'verbose_name': 'DeliveryTaskState',
                'verbose_name_plural': 'DeliveryTaskStates',
            },
        ),
        migrations.CreateModel(
            name='DeliveryTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=180, unique=True)),
                ('priority', models.CharField(choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], default='low', max_length=10)),
                ('creation_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(limit_choices_to={'is_delivery_person': False, 'is_storage_manager': True}, on_delete=django.db.models.deletion.CASCADE, related_name='created_by_sm', to=settings.AUTH_USER_MODEL)),
                ('state', models.ManyToManyField(through='core.DeliveryStateTransition', to='core.DeliveryTaskState')),
            ],
            options={
                'verbose_name': 'DeliveryTask',
                'verbose_name_plural': 'DeliveryTasks',
            },
        ),
        migrations.AddField(
            model_name='deliverystatetransition',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.DeliveryTaskState'),
        ),
        migrations.AddField(
            model_name='deliverystatetransition',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.DeliveryTask'),
        ),
    ]
