# Generated by Django 5.1.6 on 2025-02-14 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='phone',
            field=models.CharField(default=0, max_length=10, unique=True),
        ),
    ]
