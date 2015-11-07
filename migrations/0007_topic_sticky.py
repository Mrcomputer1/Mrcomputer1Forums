# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Forum', '0006_auto_20151028_2237'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='sticky',
            field=models.CharField(max_length=1, default='n'),
            preserve_default=False,
        ),
    ]
