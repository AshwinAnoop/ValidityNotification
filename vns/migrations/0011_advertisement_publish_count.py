# Generated by Django 4.1 on 2022-09-10 05:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vns', '0010_inappads_doc_type_notifyads_doc_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='advertisement',
            name='publish_count',
            field=models.IntegerField(default=0),
        ),
    ]
