# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('location', models.IntegerField()),
                ('name', models.CharField(max_length=200)),
                ('info', models.TextField()),
                ('latest_post_id', models.BigIntegerField()),
                ('latest_poster', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ForumUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('username', models.CharField(max_length=200)),
                ('banned', models.CharField(max_length=1)),
                ('ban_message', models.TextField()),
                ('signature', models.TextField()),
                ('rank', models.CharField(max_length=1)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('content', models.TextField()),
                ('poster', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('reporter', models.CharField(max_length=200)),
                ('report_message', models.TextField()),
                ('report_status', models.CharField(max_length=1)),
                ('reported', models.ForeignKey(to='Forum.Post')),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('location', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=200)),
                ('posted_by', models.CharField(max_length=200)),
                ('latest_post_id', models.BigIntegerField()),
                ('latest_poster', models.CharField(max_length=200)),
                ('closed', models.CharField(max_length=1)),
                ('forum', models.ForeignKey(to='Forum.Forum')),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='topic',
            field=models.ForeignKey(to='Forum.Topic'),
        ),
        migrations.AddField(
            model_name='forum',
            name='section',
            field=models.ForeignKey(to='Forum.Section'),
        ),
    ]
