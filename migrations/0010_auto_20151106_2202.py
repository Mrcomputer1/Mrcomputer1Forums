# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Forum', '0009_forumuser_scratchverify'),
    ]

    operations = [
        migrations.AddField(
            model_name='forumuser',
            name='infolocation',
            field=models.CharField(max_length=100, default='No location set'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='forumuser',
            name='infowebsitename',
            field=models.CharField(max_length=100, default='No website set'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='forumuser',
            name='infowebsiteurl',
            field=models.CharField(max_length=500, default='#'),
            preserve_default=False,
        ),
    ]
