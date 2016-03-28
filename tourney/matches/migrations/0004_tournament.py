# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-28 02:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('players', '0001_initial'),
        ('matches', '0003_auto_20160322_2233'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The public name of the tournament', max_length=100)),
                ('slug', models.SlugField(max_length=100)),
                ('players', models.ManyToManyField(to='players.Player')),
            ],
        ),
    ]