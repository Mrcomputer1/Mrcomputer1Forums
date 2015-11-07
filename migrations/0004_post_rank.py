# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Forum', '0003_remove_forumuser_banned'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='rank',
            field=models.CharField(default='', max_length=1),
            preserve_default=False,
        ),
    ]
