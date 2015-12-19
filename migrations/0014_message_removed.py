# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Forum', '0013_followedtopic'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='removed',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
