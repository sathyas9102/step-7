# Generated by Django 5.0.6 on 2025-03-01 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_remove_invoicerequest_approved_by_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('media', 'Media'), ('admin', 'Admin')], default='media', max_length=50),
        ),
    ]
