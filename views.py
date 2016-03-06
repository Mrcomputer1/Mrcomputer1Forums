from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.paginator import Paginator, InvalidPage
from datetime import datetime
from .models import *
from .forum_settings import *
import json, hashlib, math
from django.utils import timezone

def prepare(request, is_admin_page=False):
    if request.user.is_authenticated():
        FORUM_SETTINGS['MSG_COUNT_'] = Message.objects.filter(user=request.user).filter(removed=False).count()
    else:
        FORUM_SETTINGS['MSG_COUNT_'] = -1

    if request.user.is_staff or request.user.is_superuser and not Report.objects.filter(report_status='o').count() == 0 and not Report.objects.filter(report_status='r').count() == 0:
        messages.warning(request, "There are new reports", fail_silently=True)
# Create your views here.
def forumlist(request):
    prepare(request)
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
    prepare(request)
    try:
        f = Forum.objects.get(pk=forum_id)
        topics = Topic.objects.filter(forum=f).filter(sticky="n").order_by("-last_post_date")
        topics2 = Paginator(topics, 25)
        pagenum = 1
        if 'page' in request.GET:
            pagenum = request.GET['page']
        try:
            page = topics2.page(pagenum)
        except InvalidPage:
            pagenum = 1
            page = topics2.page(pagenum)
            messages.error(request, "Requested page not found", fail_silently=True)
        template = loader.get_template("topics.html")
        context = RequestContext(request, {
            'auth': request.user.is_authenticated(),
            'user': request.user,
            'forum': f,
            'topics': page.object_list, #Topic.objects.order_by('-post_date')
            'forumsettings': FORUM_SETTINGS,
            'stickys': Topic.objects.filter(forum=f).filter(sticky="y").order_by("-last_post_date"),
            'currentpage': int(pagenum),
            'hasnextpage': page.has_next(),
            'hasprevpage': page.has_previous(),
            'range': topics2.page_range,
            'nextpage': int(pagenum) + 1,
            'prevpage': int(pagenum) - 1
        })
        if Forum.objects.get(pk=forum_id).section.id == FORUM_SETTINGS['STAFF_SECTION'] and not request.user.is_staff:
            raise PermissionDenied
        else:
            return HttpResponse(template.render(context))
    except Forum.DoesNotExist:
        raise Http404("Forum not found")

def logouttask(request):
    prepare(request)
    logout(request)
    messages.success(request, "You have been logged out! Goodbye!", fail_silently=True)
    return redirect(FORUM_SETTINGS['FORUM_ROOT'])

def loginaccount(request):
    prepare(request)
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
    prepare(request)
    if request.method == "POST":
        u = User.objects.create_user(request.POST['user'], request.POST['email'], request.POST['pass'])
        u.save()
        forumuser = ForumUser(username=request.POST['user'], ban_message='', signature='No about me set', user=u, rank='u')
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
    prepare(request)
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
    prepare(request)
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
    prepare(request)
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
                msg = Message(removed=False, admin_message=False, content='New posts in [url](link)' + FORUM_SETTINGS['FORUM_ROOT'] + 'post/' + str(p.id) + '/(/link)' + t.name + '[/url]' , user=ft.user, date=datetime.now())
                msg.save()
            posts = Post.objects.filter(topic=t).order_by("post_date")
            posts2 = Paginator(posts, 10)
            return redirect("/topic/" + str(t.id) + "/?page=" + str(posts2.num_pages) + "#post-" + str(p.id))
        
        t = Topic.objects.get(pk=topic_id)
        posts = Post.objects.filter(topic=t).order_by("post_date")
        posts2 = Paginator(posts, 10)
        pagenum = 1
        if 'page' in request.GET:
            pagenum = request.GET["page"]
        try:
            page = posts2.page(pagenum)
        except InvalidPage:
            messages.error(request, "Requested page not found", fail_silently=True)
            pagenum = 1
            page = posts2.page(pagenum)
        
        template = loader.get_template("viewtopic.html")
        context = RequestContext(request, {
            'auth': request.user.is_authenticated(),
            'user': request.user,
            'forumsettings': FORUM_SETTINGS,
            'topics': t,
            'posts': page.object_list, #Post.objects.order_by('post_date')
            'Copen': "o",
            'Cclose': "c",
            'range': posts2.page_range,
            'currentpage': int(pagenum),
            'hasnextpage': page.has_next,
            'hasprevpage': page.has_previous(),
            'nextpage': int(pagenum) + 1,
            'prevpage': int(pagenum) - 1
        })
        return HttpResponse(template.render(context))
    except Topic.DoesNotExist:
        raise Http404("Topic not found")

def deletepost(request, post_id):
    prepare(request)
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
    prepare(request)
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
    prepare(request)
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
    prepare(request)
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
    prepare(request)
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
    prepare(request)
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
    prepare(request)
    try:
        p = Post.objects.get(pk=post_id)
        count = Post.objects.filter(topic=p.topic).filter(post_date__lt=p.post_date).count() + 1
        page = math.ceil(count / float(10))
        return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "topic/" + str(p.topic.id) + "/?page=" + str(page) + "#post-" + str(p.id))
    except Post.DoesNotExist:
        raise Http404("Post not found")

def changepassword(request):
    prepare(request)
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
    prepare(request)
    if request.method == "POST":
        if request.user.is_authenticated():
            r = Report(reporter=request.user.username, reported=Post.objects.get(pk=post_id), report_message=request.POST['message'], report_status="o", report_date=datetime.now())
            r.save()
            messages.success(request, "Post reported! Thanks for the report", fail_silently=True)
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
    prepare(request)
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
    prepare(request)
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
    prepare(request)
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
    prepare(request)
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
    prepare(request)
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
    prepare(request)
    template = loader.get_template("404.html")
    context = RequestContext(request, {
        'auth': request.user.is_authenticated(),
        'user': request.user,
        'forumsettings': FORUM_SETTINGS,
    })
    return HttpResponse(template.render(context))

def http403(request):
    prepare(request)
    template = loader.get_template("403.html")
    context = RequestContext(request, {
        'auth': request.user.is_authenticated(),
        'user': request.user,
        'forumsettings': FORUM_SETTINGS,
    })
    return HttpResponse(template.render(context))

def http500(request):
    prepare(request)
    return HttpResponse("<h1>Internal Server Error - HTTP 500</h1>")

#def admin(request):
#    prepare(request)
#    if not request.user.is_staff:
#       raise PermissionDenied 
#    
#    if request.GET['task'] == 'sidebar':
#        template = loader.get_template("admin/sidebar.html")
#        context = RequestContext(request, {
#            'user': request.user,
#            'forumsettings': FORUM_SETTINGS,
#        })
#        return HttpResponse(template.render(context))
#    elif request.GET['task'] == 'adminblank':
#        return HttpResponse("<h1>Select an area</h1>")
#    else:
#        return render(request, "admin.html")

def sticktopic(request, topic_id, stick_unstick):
    prepare(request)
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
    prepare(request)
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
    prepare(request)
    logout(request)
    template = loader.get_template("accountdeleted.html")
    context = RequestContext(request, {
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS,
    })
    return HttpResponse(template.render(context))

def admindelete(request, username):
    prepare(request)
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
    prepare(request)
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
    prepare(request)
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
    prepare(request)
    msg = Message.objects.get(pk=msg_id)
    if msg.admin_message:
        msg.removed = True
        msg.save()
    else:
        msg.delete()
    messages.success(request, "Message deleted", fail_silently=True)
    return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "messages/")

def sendmsg(request, username):
    prepare(request)
    if request.method == "POST":
        if request.user.is_staff:
            msg = Message(removed=False, admin_message=True, content=request.POST['content'], user=User.objects.get(username=username), date=datetime.now())
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
    prepare(request)
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

def adminmessages(request, username):
    prepare(request)
    if request.user.is_staff:
        template = loader.get_template("reviewadminmessages.html")
        context = RequestContext(request, {
            'user': request.user,
            'auth': request.user.is_authenticated(),
            'forumsettings': FORUM_SETTINGS,
            'sentmessages': Message.objects.filter(user=User.objects.get(username=username)).order_by('-date'),
        })
        return HttpResponse(template.render(context))
    else:
        raise PermissionDenied

def deleteadminmsg(request, username, mid):
    prepare(request)
    if request.user.is_staff:
        m = Message.objects.get(pk=mid)
        m.delete()
        messages.success(request, "Deleted admin message", fail_silently=True)
        return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "user/" + username + "/admin_messages/")
    else:
        raise PermissionDenied
    
def viewposts(request, username):
    # Links to this page are not shown to normal users but normal users can
    # see this page
    prepare(request)
    posts = Post.objects.filter(poster=username).order_by('-post_date')
    posts2 = Paginator(posts, 20)
    try:
        if not 'page' in request.GET:
            pagenum = 1
        else:
            pagenum = request.GET['page']
        page = posts2.page(pagenum)
    except InvalidPage:
        pagenum = 1
        page = posts2.page(pagenum)
        messages.error(request, "Requested page not found", fail_silently=True)
    template = loader.get_template("viewpostlist.html")
    context = RequestContext(request, {
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS,
        'posts': page.object_list,
        'range': posts2.page_range,
        'hasnextpage': page.has_next(),
        'hasprevpage': page.has_previous(),
        'nextpage': int(pagenum) + 1,
        'prevpage': int(pagenum) - 1,
        'currentpage': int(pagenum),
        'username': username,
    })
    messages.info(request, "Post count: " + str(Post.objects.filter(poster=username).count()), fail_silently=True)
    return HttpResponse(template.render(context))

def install(request):
    prepare(request)
    if not User.objects.count() == 0:
        raise Http404("Already installed!")
    if request.method == "POST":
        u = User.objects.create_user(request.POST['user'], 'noEmailSet@example.org', request.POST['pass'])
        u.is_staff = True
        u.is_superuser = True
        u.save()
        forumuser = ForumUser(username=request.POST['user'], ban_message='', signature='No about me set', user=u, rank='a')
        forumuser.save()
        return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "install/complete/")

    template = loader.get_template("install.html")
    context = RequestContext(request, {
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS,
    })
    return HttpResponse(template.render(context))

def installComplete(request):
    prepare(request)
    template = loader.get_template("installed.html")
    context = RequestContext(request, {
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS,
    })
    return HttpResponse(template.render(context))

def deletealluserposts(request, username):
    prepare(request)
    if request.method == "POST":
        if request.user.is_staff or request.user.is_superuser:
            if not request.POST['action'] == "Delete all posts and leave place holder":
                p = Post.objects.filter(poster=username)
                for post in p:
                    post.delete()
            else:
                p = Post.objects.filter(poster=username)
                for post in p:
                    post.content = "[i]Post deleted[/i]"
                    post.rank = "d"
                    post.save()
            messages.success(request, 'All posts have been deleted', fail_silently=True)
            return redirect(FORUM_SETTINGS['FORUM_ROOT'])
        else:
            raise PermissionDenied
    else:
        template = loader.get_template("deleteallposts.html")
        context = RequestContext(request, {
            'user': request.user,
            'auth': request.user.is_authenticated(),
            'forumsettings': FORUM_SETTINGS,
            'username': username,
        })
        if request.user.is_staff or request.user.is_superuser:
            return HttpResponse(template.render(context))
        else:
            raise PermissionDenied

def regenpostranks(request, username):
    if request.user.is_staff or request.user.is_superuser:
        for post in Post.objects.filter(poster=username):
            user = User.objects.get(username=username)
            if user.is_superuser:
                post.rank = "a"
            elif user.is_staff:
                post.rank = "m"
            else:
                post.rank = "u"
            post.save()
        messages.success(request, "Refreshed post ranks", fail_silently=True)
        return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "user/" + username)
    else:
        raise PermissionDenied

###
#:ADMIN
###

def admin_home(request):
    prepare(request, is_admin_page=True)
    if not request.user.is_staff:
        raise PermissionDenied
    template = loader.get_template("_admin/home.html")
    context = RequestContext(request, {
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS,
        'open_reports': Report.objects.filter(report_status="o").count(),
        'review_reports': Report.objects.filter(report_status="r").count(),
        'closed_reports': Report.objects.filter(report_status="c").count(),
        'reports': Report.objects.count(),
        'topics': Topic.objects.count(),
        'posts': Post.objects.count(),
        'users': ForumUser.objects.count(),
    })
    return HttpResponse(template.render(context))

def admin_forumlist(request):
    prepare(request, is_admin_page=True)
    if not request.user.is_superuser:
        raise PermissionDenied
    template = loader.get_template("_admin/forums.html")
    context = RequestContext(request, {
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS,
        'sections': Section.objects.order_by("location"),
        'forums': Forum.objects.order_by("location"),
    })
    return HttpResponse(template.render(context))

def admin_sectionmanage(request, section):
    prepare(request, is_admin_page=True)
    if not request.user.is_superuser:
        raise PermissionDenied
    saved = False
    if request.method == "POST":
        sectionobj2 = Section.objects.get(pk=section)
        sectionobj2.name = request.POST['section_name']
        sectionobj2.location = request.POST['section_location']
        sectionobj2.save()
        saved = True
    sectionobj = Section.objects.get(pk=section)
    template = loader.get_template("_admin/sectionmanage.html")
    context = RequestContext(request, {
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS,
        'section': sectionobj,
        'is_creating': False,
        'is_saved': saved
    })
    return HttpResponse(template.render(context))

def admin_sectioncreate(request):
    prepare(request, is_admin_page=True)
    if not request.user.is_superuser:
        raise PermissionDenied
    saved = False
    if request.method == "POST":
        sectionobj2 = Section(name=request.POST['section_name'], location=int(request.POST['section_location']))
        sectionobj2.save()
        saved = True
        return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "_admin")
    template = loader.get_template("_admin/sectionmanage.html")
    context = RequestContext(request, {
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS,
        'is_creating': True,
        'is_saved': saved
    })
    return HttpResponse(template.render(context))

def admin_section_delete(request, section):
    prepare(request, is_admin_page=True)
    if not request.user.is_superuser:
        raise PermissionDenied
    deleted = False
    if request.method == "POST":
        if request.POST['delete'] == "Delete":
            Section.objects.get(pk=section).delete()
            deleted = True
    template = loader.get_template("_admin/confirm_section_delete.html")
    if not deleted:
        context = RequestContext(request, {
            'deleted': False,
            'section': Section.objects.get(pk=section),
            'forumsettings': FORUM_SETTINGS,
            'user': request.user,
            'auth': request.user.is_authenticated()
        })
    else:
        context = RequestContext(request, {
            'deleted': True,
            'forumsettings': FORUM_SETTINGS,
            'user': request.user,
            'auth': request.user.is_authenticated()
        })
    return HttpResponse(template.render(context))

def admin_forummanage(request, forum):
    prepare(request, is_admin_page=True)
    if not request.user.is_superuser:
        raise PermissionDenied
    saved = False
    if request.method == "POST":
        forum_ = Forum.objects.get(pk=forum)
        forum_.name = request.POST['name']
        forum_.location = int(request.POST['location'])
        forum_.info = request.POST['info']
        forum_.save()
        saved = True
    template = loader.get_template("_admin/forummanage.html")
    context = RequestContext(request, {
        'forum': Forum.objects.get(pk=forum),
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS,
        'is_saved': saved,
        'is_creating': False
    })
    return HttpResponse(template.render(context))

def admin_forumcreate(request):
    prepare(request, is_admin_page=True)
    if not request.user.is_superuser:
        raise PermissionDenied
    saved = False
    if request.method == "POST":
        forum = Forum(name=request.POST['name'], location = int(request.POST['location']), info = request.POST['info'], section=Section.objects.get(pk=request.GET['section']), latest_post_id=0, latest_poster='')
        forum.save()
        saved = True
        return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "_admin")
    template = loader.get_template("_admin/forummanage.html")
    context = RequestContext(request, {
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS,
        'is_creating': True,
        'is_saved': saved,
        'sectionid': request.GET['section']
    })
    return HttpResponse(template.render(context))

def admin_forum_delete(request, forumid):
    prepare(request, is_admin_page=True)
    if not request.user.is_superuser:
        raise PermissionDenied
    deleted = False
    if request.method == "POST":
        if request.POST['delete'] == "Delete":
            Forum.objects.get(pk=forumid).delete()
            deleted = True
    template = loader.get_template("_admin/confirm_forum_delete.html")
    if not deleted:
        context = RequestContext(request, {
            'deleted': False,
            'forum': Forum.objects.get(pk=forumid),
            'forumsettings': FORUM_SETTINGS,
            'user': request.user,
            'auth': request.user.is_authenticated()
        })
    else:
        context = RequestContext(request, {
            'deleted': True,
            'forumsettings': FORUM_SETTINGS,
            'user': request.user,
            'auth': request.user.is_authenticated()
        })
    return HttpResponse(template.render(context))

def admin_reports(request):
    prepare(request, is_admin_page=True)
    if not request.user.is_staff:
        raise PermissionDenied
    template = loader.get_template("_admin/reports.html")
    context = RequestContext(request, {
        "reviewreports": Report.objects.filter(report_status="r"),
        "openreports": Report.objects.filter(report_status="o"),
        "forumsettings": FORUM_SETTINGS,
        "user": request.user,
        "auth": request.user.is_authenticated()
    })
    return HttpResponse(template.render(context))

def admin_report_review(request, report):
    prepare(request, is_admin_page=True)
    if not request.user.is_staff:
        raise PermissionDenied
    reportobj = Report.objects.get(pk=report)
    reportobj.report_status = "r"
    reportobj.save()
    return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "_admin/reports")

def admin_report_close(request, report):
    prepare(request, is_admin_page=True)
    if not request.user.is_staff:
        raise PermissionDenied
    reportobj = Report.objects.get(pk=report)
    reportobj.report_status = "c"
    reportobj.save()
    return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "_admin/reports")

def admin_tools(request):
    prepare(request, is_admin_page=True)
    if not request.user.is_staff:
        raise PermissionDenied
    template = loader.get_template("_admin/tools.html")
    context = RequestContext(request, {
        'user': request.user,
        'auth': request.user.is_authenticated(),
        'forumsettings': FORUM_SETTINGS
    })
    return HttpResponse(template.render(context))

def admin_tools_refresh_post_ranks(request):
    prepare(request, is_admin_page=True)
    if not request.user.is_staff:
        raise PermissionDenied
    for post in Post.objects.all():
        user = User.objects.get(username=post.poster)
        if user.is_superuser:
            post.rank = "a"
        elif user.is_staff:
            post.rank = "m"
        else:
            post.rank = "u"
        post.save()
    return redirect(FORUM_SETTINGS['FORUM_ROOT'] + "_admin/tools")
