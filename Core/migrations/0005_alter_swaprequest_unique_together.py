# Generated by Django 5.1.6 on 2025-02-20 12:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0003_student_reset_token'),
        ('Core', '0004_swaprequest'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='swaprequest',
            unique_together={('sender', 'receiver', 'skill')},
        ),
    ]
