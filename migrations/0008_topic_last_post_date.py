# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Forum', '0007_topic_sticky'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='last_post_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 31, 4, 58, 17, 263264, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
