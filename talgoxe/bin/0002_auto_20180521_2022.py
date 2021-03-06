# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-21 18:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('talgoxe', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Artikel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lemma', models.CharField(max_length=100)),
                ('rang', models.SmallIntegerField()),
                ('skapat', models.DateTimeField(auto_now_add=True)),
                ('uppdaterat', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Spole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=2000)),
                ('pos', models.SmallIntegerField()),
                ('skapat', models.DateTimeField(auto_now_add=True)),
                ('uppdaterat', models.DateTimeField(auto_now=True)),
                ('artikel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='talgoxe.Artikel')),
            ],
        ),
        migrations.CreateModel(
            name='Typ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kod', models.CharField(max_length=5)),
                ('namn', models.CharField(max_length=30)),
                ('skapat', models.DateTimeField(auto_now_add=True)),
                ('uppdaterat', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='data',
            name='lemma',
        ),
        migrations.RemoveField(
            model_name='data',
            name='type',
        ),
        migrations.DeleteModel(
            name='Data',
        ),
        migrations.DeleteModel(
            name='Lemma',
        ),
        migrations.DeleteModel(
            name='Type',
        ),
        migrations.AddField(
            model_name='spole',
            name='typ',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='talgoxe.Typ'),
        ),
    ]
