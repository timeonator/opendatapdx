# Generated by Django 2.1.2 on 2018-10-29 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cataloger', '0003_dataset_contactpoint'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='rights',
            field=models.TextField(blank=True),
        ),
    ]
