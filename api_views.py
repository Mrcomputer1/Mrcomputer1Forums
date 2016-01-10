from django.shortcuts import redirect, render
from django.http import HttpResponse
from .models import *
from .forum_settings import *
import json
from django.contrib.auth.models import User
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

def api(request):
    return redirect("http://mrcomputer1forums.github.io/docs/#api/home")

####################
##### API V1   #####
####################
def v1(request):
    r = {"api-version": "v1", "api-path": FORUM_SETTINGS['FORUM_ROOT'] + "api/v1/"}
    return HttpResponse(json.dumps(r))

def v1_info(request):
    r = {"name": FORUM_SETTINGS['FORUM_NAME'], "root": FORUM_SETTINGS['FORUM_ROOT'],
         "admin": FORUM_SETTINGS['SITE_ADMIN'], "newsforumid": FORUM_SETTINGS['NEWS_FORUM'],
         "alert": {"enabled": FORUM_SETTINGS['ALERT_ON'], "msg": FORUM_SETTINGS['ALERT_MSG']}}
    return HttpResponse(json.dumps(r))

def v1_user_username(request, username):
    try:
        u = User.objects.get(username=username)
        f = ForumUser.objects.get(user=u)
        r = {"username": u.username, "rank": f.rank, "about": f.signature,
             "info": {"location": f.infolocation, "website": {
                 "url": f.infowebsiteurl,
                 "name": f.infowebsitename}}}
        return HttpResponse(json.dumps(r))
    except ObjectDoesNotExist:
        r = {"failed": True, "http": ["404", "Not Found"],
             "human": "This user was not found"}
        return HttpResponse(json.dumps(r))

def v1_post(request, post_id):
    try:
        p = Post.objects.get(pk=post_id)
        r = {"topic": p.topic.id, "content": p.content, "posted_by": p.poster,
             "rank": ForumUser.objects.get(username=p.poster).username}
        return HttpResponse(json.dumps(r))
    except ObjectDoesNotExist:
        r = {"failed": True, "http": ["404", "Not Found"],
             "human": "This post was not found"}
        return HttpResponse(json.dumps(r))

def v1_topic(request, topic_id):
    try:
        t = Topic.objects.get(pk=topic_id)
        p = Post.objects.filter(topic=t).order_by("-post_date")
        mainpost = Post.objects.filter(topic=t).order_by("post_date")[0]
        pr = []
        for post in p:
            pr.append(post.id)
        r = {"forum": t.forum.id, "name": t.name, "posted_by": t.posted_by,
             "closed": t.closed, "sticky": t.sticky, "posts": pr, "mainpost": mainpost.id}
        return HttpResponse(json.dumps(r))
    except ObjectDoesNotExist:
        r = {"failed": True, "http": ["404", "Not Found"],
             "human": "This topic was not found"}
        return HttpResponse(json.dumps(r))

def v1_forum(request, forum_id):
    try:
        f = Forum.objects.get(pk=forum_id)
        t = Topic.objects.filter(forum=f).order_by("-post_date")
        tr = []
        for topic in t:
            tr.append(topic.id)
        r = {"section": f.section.name, "name": f.name, "info": f.info, "topics": tr}
        return HttpResponse(json.dumps(r))
    except ObjectDoesNotExist:
        r = {"failed": True, "http": ["404", "Not Found"],
             "human": "This forum was not found"}
        return HttpResponse(json.dumps(r))
