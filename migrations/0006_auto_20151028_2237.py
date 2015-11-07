# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Forum', '0005_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='owner',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
    ]
