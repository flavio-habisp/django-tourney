# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-22 21:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bracket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The public name for the bracket', max_length=100)),
                ('slug', models.SlugField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='match',
            name='bracket',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='matches.Bracket'),
            preserve_default=False,
        ),
    ]
