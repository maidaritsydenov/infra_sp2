# Generated by Django 2.2.16 on 2022-09-10 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_auto_20220909_1504'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='review',
            constraint=models.UniqueConstraint(fields=('title_id', 'author'), name='unique_review_per_title'),
        ),
    ]