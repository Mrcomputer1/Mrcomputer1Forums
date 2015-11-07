# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Forum', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='post_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 18, 8, 3, 56, 146935, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='report',
            name='report_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 18, 8, 4, 1, 45949, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='topic',
            name='post_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 18, 8, 4, 3, 342912, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
