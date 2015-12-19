from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ForumUser(models.Model):
    def __str__(m):
        return "[" + m.rank + "] " + m.username
    username = models.CharField(max_length=200)
    ban_message = models.TextField()
    signature = models.TextField()
    user = models.ForeignKey(User)
    rank = models.CharField(max_length=1) # u = User, m = Mod, a = Admin
    infolocation = models.CharField(max_length=100)
    infowebsiteurl = models.CharField(max_length=500)
    infowebsitename = models.CharField(max_length=100)

class Section(models.Model):
    def __str__(m):
        return m.name
    name = models.CharField(max_length=200)
    location = models.IntegerField()

class Forum(models.Model):
    def __str__(m):
        return "[" + m.section.name + "] " + m.name
    section = models.ForeignKey(Section)
    location = models.IntegerField()
    name = models.CharField(max_length=200)
    info = models.TextField()
    latest_post_id = models.BigIntegerField()
    latest_poster = models.CharField(max_length=200)

class Topic(models.Model):
    def __str__(m):
        return "[" + m.forum.section.name + "/" + m.forum.name + "] " + m.name + " by " + m.posted_by
    forum = models.ForeignKey(Forum)
    name = models.CharField(max_length=200)
    posted_by = models.CharField(max_length=200)
    latest_post_id = models.BigIntegerField()
    latest_poster = models.CharField(max_length=200)
    closed = models.CharField(max_length=1)
    post_date = models.DateTimeField()
    sticky = models.CharField(max_length=1)
    last_post_date = models.DateTimeField()

class Post(models.Model):
    def __str__(m):
        return "[" + m.topic.forum.section.name + "/" + m.topic.forum.name + "/" + m.topic.name + "] " + m.poster
    topic = models.ForeignKey(Topic)
    content = models.TextField()
    poster = models.CharField(max_length=200)
    post_date = models.DateTimeField()
    rank = models.CharField(max_length=1)

class Report(models.Model):
    def __str__(m):
        if m.report_status == "o":
            return "* Open Report"
        elif m.report_status == "c":
            return "Closed Report"
        elif m.report_status == "r":
            return "# Review report"
        else:
            return "@ Invaild report"
    reporter = models.CharField(max_length=200)
    reported = models.ForeignKey(Post)
    report_message = models.TextField()
    report_status = models.CharField(max_length=1)
    report_date = models.DateTimeField()

class Message(models.Model):
    admin_message = models.BooleanField()
    removed = models.BooleanField()
    content = models.TextField()
    user = models.ForeignKey(User)
    date = models.DateTimeField()

class FollowedTopic(models.Model):
    user = models.ForeignKey(User)
    topic = models.ForeignKey(Topic)
