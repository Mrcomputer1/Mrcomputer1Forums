# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Forum', '0010_auto_20151106_2202'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='forumuser',
            name='scratchverify',
        ),
    ]
