# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Forum', '0008_topic_last_post_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='forumuser',
            name='scratchverify',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
