# Generated by Django 5.1.6 on 2025-03-11 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='subject',
            field=models.IntegerField(choices=[(0, 'Computing'), (1, 'Engineering'), (2, 'Mathematics'), (3, 'Sciences'), (4, 'Medicine'), (5, 'Languages'), (6, 'Humanities'), (10, 'Other')], default=10),
            preserve_default=False,
        ),
    ]
