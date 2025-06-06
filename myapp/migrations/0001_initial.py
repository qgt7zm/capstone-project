# Generated by Django 5.1.6 on 2025-02-24 03:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('year', models.IntegerField()),
                ('publisher', models.CharField(blank=True, max_length=200)),
                ('url', models.CharField(blank=True, max_length=400)),
                ('summary', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResourceAuthor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.author')),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.resource')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('resource', 'order')},
            },
        ),
        migrations.AddField(
            model_name='resource',
            name='authors',
            field=models.ManyToManyField(related_name='resources', through='myapp.ResourceAuthor', to='myapp.author'),
        ),
    ]
