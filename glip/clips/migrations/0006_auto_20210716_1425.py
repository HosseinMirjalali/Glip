# Generated by Django 3.1.12 on 2021-07-16 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clips', '0005_auto_20210714_1346'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='gamefollow',
            constraint=models.UniqueConstraint(fields=('following', 'followed'), name='unique_followers'),
        ),
    ]
