from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from datetime import datetime
from .models import *
from .forum_settings import *
import json, hashlib
from django.utils import timezone

# Create your views here.
def forumlist(request):
    template = loader.get_template("index.html")
    context = RequestContext(request, {
        'auth': request.user.is_authenticated(),
        'user': request.user,
        'sections': Section.objects.order_by("location"),
        'forums': Forum.objects.order_by("location"),
        'forumsettings': FORUM_SETTINGS,
    })
    return HttpResponse(template.render(context))

def topiclist(request, forum_id):
    try:
        f = Forum.objects.get(pk=forum_id)
        template = loader.get_template("topics.html")
        context = RequestContext(request, {
            'auth': request.user.is_authenticated(),
            'user': request.user,
            'forum': f,
            'topics': Topic.objects.filter(forum=f).filter(sticky="n").order_by("-last_post_date"), #Topic.objects.order_by('-post_date')
            'forumsettings': FORUM_SETTINGS,
            'stickys': Topic.objects.filter(forum=f).filter(sticky="y").order_by("-last_post_date"),
        })
        if Forum.objects.get(pk=forum_id).section.id == FORUM_SETTINGS['STAFF_SECTION'] and not request.user.is_staff:
            raise PermissionDenied
        else:
            return HttpResponse(template.render(context))
    except Forum.DoesNotExist:
        raise Http404("Forum not found")

def logouttask(request):
    logout(request)
    messages.success(request, "You have been logged out! Goodbye!", fail_silently=True)
    return redirect(FORUM_SETTINGS['FORUM_ROOT'])

def loginaccount(request):
    if request.method == "POST":
        user = authenticate(username=request.POST['user'], password=request.POST['pass'])
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, 'You have been logged in as ' + user.username + "!", fail_silently=True)
                return redirect(FORUM_SETTINGS['FORUM_ROOT'])
            else:
                template = loader.get_template("banned.html")
                context = RequestContext(request, {
                    'auth': request.user.is_authenticated(),
                    'user': request.user,
                    'forumsettings': FORUM_SETTINGS,
                    'ban_msg': ForumUser.objects.get(username=user.username).ban_message,
                })
                return HttpResponse(template.render(context))
        else:
            messages.error(request, "Invalid username or password", fail_silently=True)
            return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "account/login/") 
    
    template = loader.get_template("login.html")
    context = RequestContext(request, {
        'auth': request.user.is_authenticated(),
        'user': request.user,
        'forumsettings': FORUM_SETTINGS,
    })
    if request.user.is_authenticated():
        raise PermissionDenied
    else:
        return HttpResponse(template.render(context))

def registeraccount(request):
    if request.method == "POST":
        u = User.objects.create_user(request.POST['user'], request.POST['email'], request.POST['pass'])
        u.save()
        forumuser = ForumUser(username=request.POST['user'], scratchverify=False, ban_message='', signature='No about me set', user=u, rank='u')
        forumuser.save()
        messages.success(request, "Account created! You can now log in below", fail_silently=True)
        return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "account/login/")
    
    template = loader.get_template("register.html")
    context = RequestContext(request, {
        'auth': request.user.is_authenticated(),
        'user': request.user,
        'forumsettings': FORUM_SETTINGS,
    })
    if request.user.is_authenticated():
        raise PermissionDenied
    else:
        return HttpResponse(template.render(context))

def changesignature(request, username):
    if request.method == "POST":
        if not username == request.user.username and not request.user.is_staff:
            raise PermissionDenied
        fu = ForumUser.objects.get(username=username)
        fu.signature = request.POST['signature']
        fu.save()
        messages.success(request, "About me updated!", fail_silently=True)
        return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "settings/" + username + "/")

    template = loader.get_template("changesignature.html")
    context = RequestContext(request, {
        'auth': request.user.is_authenticated(),
        'user': request.user,
        'forumsettings': FORUM_SETTINGS,
        'signature': ForumUser.objects.get(username=username).signature,
    })
    if not request.user.is_authenticated():
        raise PermissionDenied
    elif username == request.user.username:
        return HttpResponse(template.render(context))
    elif request.user.is_staff:
        return HttpResponse(template.render(context))
    else:
        raise PermissionDenied
    
def newtopic(request, forum_id):
    try:
        if request.method == "POST":
            if forum_id == FORUM_SETTINGS['NEWS_FORUM'] and not request.user.is_staff:
                raise PermissionDenied
            
            if request.user.is_superuser:
                rank = "a"
            elif request.user.is_staff:
                rank = "m"
            else:
                rank = "u"
            t = Topic(forum=Forum.objects.get(pk=forum_id), name=request.POST['name'], posted_by=request.user.username, latest_post_id=0, latest_poster=0, closed='o', post_date=datetime.now(), last_post_date=timezone.now(), sticky="n")
            t.save()
            p = Post(topic=t, content=request.POST['content'], rank=rank, poster=request.user.username, post_date=datetime.now())
            p.save()
            messages.success(request, "Created topic!", fail_silently=True)
            return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "topic/" + str(t.id) + "/")
        
        template = loader.get_template("newtopic.html")
        context = RequestContext(request, {
            'auth': request.user.is_authenticated(),
            'user': request.user,
            'forumsettings': FORUM_SETTINGS,
        })
        if not request.user.is_authenticated():
            raise PermissionDenied
        else:
            if forum_id == FORUM_SETTINGS['NEWS_FORUM'] and not request.user.is_staff:
                raise PermissionDenied
            return HttpResponse(template.render(context))
    except Forum.DoesNotExist:
        raise Http404("Forum not found")

def viewtopic(request, topic_id):
    try:
        if request.method == "POST":
            if request.user.is_superuser:
                rank = "a"
            elif request.user.is_staff:
                rank = "m"
            else:
                rank = "u"
            p = Post(topic=Topic.objects.get(pk=topic_id), content=request.POST['content'], poster=request.user.username, post_date=datetime.now(), rank=rank)
            p.save()
            t = Topic.objects.get(pk=topic_id)
            t.last_post_date = timezone.now()
            t.save()
            for ft in FollowedTopic.objects.filter(topic=t):
                msg = Message(admin_message=False, content='New posts in [url](link)' + FORUM_SETTINGS['FORUM_ROOT'] + 'post/' + str(p.id) + '/(/link)' + t.name + '[/url]' , user=ft.user, date=datetime.now())
                msg.save()

        t = Topic.objects.get(pk=topic_id)
        template = loader.get_template("viewtopic.html")
        context = RequestContext(request, {
            'auth': request.user.is_authenticated(),
            'user': request.user,
            'forumsettings': FORUM_SETTINGS,
            'topics': t,
            'posts': Post.objects.filter(topic=t).order_by("post_date"), #Post.objects.order_by('post_date')
            'Copen': "o",
            'Cclose': "c",
        })
        return HttpResponse(template.render(context))
    except Topic.DoesNotExist:
        raise Http404("Topic not found")

def deletepost(request, post_id):
    if request.user.is_staff:
        if FORUM_SETTINGS['BIN_TOPIC'] == -1:
            p = Post.objects.get(pk=post_id)
            p.delete()
        else:
            t = Topic.objects.get(pk=FORUM_SETTINGS['BIN_TOPIC'])
            p = Post.objects.get(pk=post_id)
            if p.topic == t:
                p.delete()
                return redirect(FORUM_SETTINGS['FORUM_ROOT'])
            p.topic = t
            p.save()
        messages.success(request, "Post deleted!", fail_silently=True)
        return redirect(FORUM_SETTINGS['FORUM_ROOT'])
    else:
        raise PermissionDenied

def deletetopic(request, topic_id):
    if request.user.is_staff:
        if FORUM_SETTINGS['BIN_FORUM'] == -1:
            t = Topic.objects.get(pk=topic_id)
            t.delete()
        else:
            f = Forum.objects.get(pk=FORUM_SETTINGS['BIN_FORUM'])
            t = Topic.objects.get(pk=topic_id)
            if t.forum == f:
                t.delete()
                return redirect(FORUM_SETTINGS['FORUM_ROOT'])
            t.forum = f
            t.save()
            messages.success(request, "Topic deleted!", fail_silently=True)
        return redirect(FORUM_SETTINGS['FORUM_ROOT'])
    else:
        raise PermissionDenied

def openclosetopic(request, topic_id, open_close):
    if request.user.is_staff:
        if open_close == "o":
            t = Topic.objects.get(pk=topic_id)
            t.closed = "o"
            t.save()
            messages.success(request, "Topic opened!", fail_silently=True)
        elif open_close == "c":
            t = Topic.objects.get(pk=topic_id)
            t.closed = "c"
            t.save()
            messages.success(request, "Topic closed!", fail_silently=True)
        else:
            raise SyntaxError("Please pick a vaild action! O for open, C for close")
        return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "topic/" + str(topic_id) + "/")
    else:
        raise PermissionDenied
def movetopic(request, topic_id):
    if request.user.is_staff:
        if request.method == "POST":
            t = Topic.objects.get(pk=topic_id)
            t.forum = Forum.objects.get(pk=request.POST['forum'])
            t.save()
            messages.success(request, "Topic moved!", fail_silently=True)
            return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "topic/" + str(topic_id) + "/")
        
        template = loader.get_template("movetopic.html")
        context = RequestContext(request, {
            'auth': request.user.is_authenticated(),
            'user': request.user,
            'forumsettings': FORUM_SETTINGS,
            'forums': Forum.objects.order_by('location'),
        })
        return HttpResponse(template.render(context))
    else:
        raise PermissionDenied

def movepost(request, post_id):
    if request.user.is_staff:
        if request.method == "POST":
            p = Post.objects.get(pk=post_id)
            p.topic = Topic.objects.get(pk=request.POST['topicid'])
            p.save()
            messages.success(request, "Post moved!", fail_silently=True)
            return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "post/" + str(post_id) + "/")

        template = loader.get_template("movepost.html")
        context = RequestContext(request, {
            'auth': request.user.is_authenticated(),
            'user': request.user,
            'forumsettings': FORUM_SETTINGS,
        })
        return HttpResponse(template.render(context))
    else:
        raise PermissionDenied

def editpost(request, post_id):
    if request.user.is_staff or Post.objects.get(pk=post_id).poster == request.user.username:
        if request.method == "POST":
            p = Post.objects.get(pk=post_id)
            p.content = request.POST['content']
            p.save()
            messages.success(request, "Updated post!", fail_silently=True)
            return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "post/" + str(post_id) + "/")

        template = loader.get_template("editpost.html")
        context = RequestContext(request, {
            'auth': request.user.is_authenticated(),
            'user': request.user,
            'forumsettings': FORUM_SETTINGS,
            'content': Post.objects.get(pk=post_id).content,
        })
        return HttpResponse(template.render(context))
    else:
        raise PermissionDenied

def gotopost(request, post_id):
    try:
        p = Post.objects.get(pk=post_id)
        return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "topic/" + str(p.topic.id) + "/#post-" + str(p.id))
    except Post.DoesNotExist:
        raise Http404("Post not found")

def changepassword(request):
    if request.method == "POST":
        if request.user.is_authenticated():
            u = authenticate(username=request.user.username, password=request.POST['oldpass'])
            if u is not None:
                 u.set_password(request.POST['password'])
                 u.save()
                 messages.success(request, "Password changed", fail_silently=True)
                 return redirect(FORUM_SETTINGS['FORUM_ROOT'])
            #else:
                #return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "account/changepassword/")
        else:
            raise PermissionDenied

    if request.user.is_authenticated():
        template = loader.get_template("changepwd.html")
        context = RequestContext(request, {
            'auth': request.user.is_authenticated(),
            'user': request.user,
            'forumsettings': FORUM_SETTINGS,
        })
    else:
        raise PermissionDenied
    return HttpResponse(template.render(context))

def report(request, post_id):
    if request.method == "POST":
        if request.user.is_authenticated():
            r = Report(reporter=request.user.username, reported=Post.objects.get(pk=post_id), report_message=request.POST['message'], report_status="o", report_date=datetime.now())
            r.save()
            message.success(request, "Post reported! Thanks for the report", fail_silently=True)
            return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "post/" + str(post_id) + "/")
        else:
            raise PermissionDenied

    if request.user.is_authenticated():
        template = loader.get_template("report.html")
        context = RequestContext(request, {
            'auth': request.user.is_authenticated(),
            'user': request.user,
            'forumsettings': FORUM_SETTINGS,
        })
    else:
        raise PermissionDenied
    return HttpResponse(template.render(context))

def renametopic(request, topic_id):
    if request.method == "POST":
        if request.user.is_authenticated():
            if request.user.is_staff:
                t = Topic.objects.get(pk=topic_id)
                t.name = request.POST['name']
                t.save()
                messages.success(request, "Renamed topic!", fail_silently=True)
                return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "topic/" + str(topic_id) + "/")
            else:
                raise PermissionDenied
        else:
            raise PermissionDenied

    if request.user.is_authenticated():
        template = loader.get_template("renametopic.html")
        context = RequestContext(request, {
            'auth': request.user.is_authenticated(),
            'user': request.user,
            'forumsettings': FORUM_SETTINGS,
            'topicname': Topic.objects.get(pk=topic_id).name,
        })
        return HttpResponse(template.render(context))
    else:
        raise PermissionDenied

def viewuser(request, username):
    try:
        template = loader.get_template("viewuser.html")
        context = RequestContext(request, {
            'auth': request.user.is_authenticated(),
            'user': request.user,
            'forumsettings': FORUM_SETTINGS,
            'pageuser': User.objects.get(username=username),
            'forumuser': ForumUser.objects.get(username=username),
        })
        return HttpResponse(template.render(context))
    except ForumUser.DoesNotExist:
        raise Http404("User not found")
    except User.DoesNotExist:
        raise Http404("User not found")

def banuser(request, username):
    if request.method == "POST":
        if request.user.is_authenticated() and request.user.is_staff:
            if request.POST['banned'] == "yes":
                u = User.objects.get(username=username)
                f = ForumUser.objects.get(username=username)
                u.is_active = False
                f.ban_message = request.POST['msg']
                u.save()
                f.save()
                messages.warning(request, "User " + u.username + " has been banned for: " + f.ban_message, fail_silently=True)
            else:
                u = User.objects.get(username=username)
                u.is_active = True
                u.save()
                messages.warning(request, "User " + u.username + " has been unbanned", fail_silently=True)
            return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "user/" + username + "/")
        else:
            raise PermissionDenied

    template = loader.get_template("banuser.html")
    context = RequestContext(request, {
        'auth': request.user.is_authenticated(),
        'user': request.user,
        'forumsettings': FORUM_SETTINGS,
        'banreason': ForumUser.objects.get(username=username).ban_message,
        'banned': User.objects.get(username=username).is_active,
    })
    if request.user.is_authenticated and request.user.is_staff:
        return HttpResponse(template.render(context))
    else:
        raise PermissionDenied

def banappeal(request):
    if request.method == "POST":
        u = authenticate(username=request.POST['user'], password=request.POST['pass'])
        if u is not None:
            if not u.is_active:
                f = ForumUser.objects.get(user=u)
                if FORUM_SETTINGS['APPEAL_FORUM'] == -1:
                    messages.error(request, "Sorry, this forum does not accept ban appeals", fail_silently=True)
                    raise PermissionDenied
                else:
                    forum = Forum.objects.get(pk=FORUM_SETTINGS['APPEAL_FORUM'])
                t = Topic(forum=forum, name=u.username + "'s ban appeal", posted_by=u.username, latest_post_id=-1,latest_poster=-1, closed="o", post_date=datetime.now())
                t.save()
                p = Post(topic=t,content=request.POST['msg'],poster=u.username,post_date=datetime.now())
                p.save()
                messages.success(request, "Appealed!", fail_silently=True)
                return redirect(FORUM_SETTINGS['FORUM_ROOT'])

    template = loader.get_template("banappeal.html")
    context = RequestContext(request, {
        'auth': request.user.is_authenticated(),
        'user': request.user,
        'forumsettings': FORUM_SETTINGS,
    })
    return HttpResponse(template.render(context))

def changerank(request, username):
    if request.method == "POST":
        if request.user.is_superuser:
            if request.POST['rank'] == "a":
                u = User.objects.get(username=username)
                u.is_superuser = True
                u.is_staff = True
                u.save()
            elif request.POST['rank'] == "m":
                u = User.objects.get(username=username)
                u.is_staff = True
                u.is_superuser = False
                u.save()
            else:
                u = User.objects.get(username=username)
                u.is_staff = False
                u.is_superuser = False
                u.save()
            messages.success(request, "Rank updated!", fail_silently=True)
            return redirect(FORUM_SETTINGS['FORUM_ROOT'])
        else:
            raise PermissionDenied

    template = loader.get_template("rankchange.html")
    context = RequestContext(request, {
        'auth': request.user.is_authenticated(),
        'user': request.user,
        'forumsettings': FORUM_SETTINGS,
    })
    if request.user.is_superuser:
        return HttpResponse(template.render(context))
    else:
        raise PermissionDenied

def http404(request):
    template = loader.get_template("404.html")
    context = RequestContext(request, {
        'auth': request.user.is_authenticated(),
        'user': request.user,
        'forumsettings': FORUM_SETTINGS,
    })
    return HttpResponse(template.render(context))

def http403(request):
    template = loader.get_template("403.html")
    context = RequestContext(request, {
        'auth': request.user.is_authenticated(),
        'user': request.user,
        'forumsettings': FORUM_SETTINGS,
    })
    return HttpResponse(template.render(context))

def http500(request):
    return HttpResponse("<h1>Internal Server Error - HTTP 500</h1>")

def admin(request):
    if not request.user.is_staff:
       raise PermissionDenied 
    
    if request.GET['task'] == 'sidebar':
        template = loader.get_template("admin/sidebar.html")
        context = RequestContext(request, {
            'user': request.user,
            'forumsettings': FORUM_SETTINGS,
        })
        return HttpResponse(template.render(context))
    elif request.GET['task'] == 'adminblank':
        return HttpResponse("<h1>Select an area</h1>")
    else:
        return render(request, "admin.html")

def sticktopic(request, topic_id, stick_unstick):
    if request.user.is_staff:
        if stick_unstick == "s":
            t = Topic.objects.get(pk=topic_id)
            t.sticky = "y"
            t.save()
            messages.success(request, "Made sticky!", fail_silently=True)
        elif stick_unstick == "u":
            t = Topic.objects.get(pk=topic_id)
            t.sticky = "n"
            t.save()
            messages.success(request, "Removed sticky!", fail_silently=True)
        else:
            raise SyntaxError("Please pick a vaild action! S for stick, U for unstick")
        return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "topic/" + str(topic_id) + "/")
    else:
        raise PermissionDenied

def deleteaccount(request):
    if request.user.is_authenticated():
        if request.method == "POST":
            fu = ForumUser.objects.get(username=request.user.username)
            u = User.objects.get(username=request.user.username)
            fu.ban_message = "Account deletion requested!"
            fu.save()
            u.is_active = False
            u.save()
            return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "account/account_deleted/")
        else:
            messages.warning(request, "Feature not complete!", fail_silently=True)
            template = loader.get_template("deleteaccount.html")
            context = RequestContext(request, {
                'user': request.user,
                'auth': request.user.is_authenticated(),
                'forumsettings': FORUM_SETTINGS,
            })
            return HttpResponse(template.render(context))
    else:
        raise PermissionDenied

def accountdeleted(request):
    logout(request)
    template = loader.get_template("accountdeleted.html")
    context = RequestContext(request, {
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS,
    })
    return HttpResponse(template.render(context))

def admindelete(request, username):
    if request.method == "POST" and request.user.is_superuser:
        User.objects.get(username=username).delete()
        messages.warning(request, "Account deleted!", fail_silently=True)
        return redirect(FORUM_SETTINGS['FORUM_ROOT'])
    template = loader.get_template("deleteuser.html")
    context = RequestContext(request, {
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS,
        'target': User.objects.get(username=username),
    })
    if request.user.is_superuser:
        return HttpResponse(template.render(context))
    else:
        raise PermissionDenied

def bbcodesource(request, post_id):
    return HttpResponse(Post.objects.get(pk=post_id).content)

def postauthor(request, post_id):
    return HttpResponse(Post.objects.get(pk=post_id).poster)

def postasjson(request, post_id):
    json1 = {"content": Post.objects.get(pk=post_id).content, "poster": Post.objects.get(pk=post_id).poster}
    json2 = json.dumps(json1)
    return HttpResponse(json2)

def settingsdetails(request, username):
    if request.method == "POST":
        if request.user.username == username or request.user.is_staff:
            f = ForumUser.objects.get(username=username)
            f.infolocation = request.POST['location']
            f.infowebsiteurl = request.POST['websiteurl']
            f.infowebsitename = request.POST['websitename']
            f.save()
            messages.success(request, "Updated!", fail_silently=True)
            return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "user/" + username + "/")
        else:
            raise PermissionDenied

    template = loader.get_template("changedetails.html")
    context = RequestContext(request, {
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS,
        'forumuser': ForumUser.objects.get(username=username),
    })
    if request.user.is_authenticated():
        return HttpResponse(template.render(context))
    else:
        raise PermissionDenied

def messagesview(request):
    template = loader.get_template("messages.html")
    context = RequestContext(request, {
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS,
        'sentmessages': Message.objects.filter(user=request.user).order_by("-date"),
    })
    if request.user.is_authenticated():
        return HttpResponse(template.render(context))
    else:
        raise PermissionDenied

def deletemsg(request, msg_id):
    msg = Message.objects.get(pk=msg_id)
    msg.delete()
    messages.success(request, "Message deleted", fail_silently=True)
    return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "messages/")

def sendmsg(request, username):
    if request.method == "POST":
        if request.user.is_staff:
            msg = Message(admin_message=True, content=request.POST['content'], user=User.objects.get(username=username), date=datetime.now())
            msg.save()
            messages.success(request, "Message sent", fail_silently=True)
            return redirect(FORUM_SETTINGS['FORUM_ROOT'])
        else:
            raise PermissionDenied

    template = loader.get_template("sendalert.html")
    context = RequestContext(request, {
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS,
    })
    if request.user.is_authenticated() and request.user.is_staff:
        return HttpResponse(template.render(context))
    else:
        raise PermissionDenied

def followunfollow(request, topic_id):
    topic = topic_id
    if request.user.is_authenticated():
        try:
            user = request.user
            follow = FollowedTopic.objects.get(user=user, topic=Topic.objects.get(pk=topic))
            follow.delete()
            messages.success(request, "Topic unfollowed", fail_silently=True)
            return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "topic/" + topic + "/")
        except ObjectDoesNotExist:
            user = request.user
            follow = FollowedTopic(user = user, topic = Topic.objects.get(pk=topic))
            follow.save()
            messages.success(request, "Topic followed", fail_silently=True)
            return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "topic/" + topic + "/")
    else:
        raise PermissionDenied
