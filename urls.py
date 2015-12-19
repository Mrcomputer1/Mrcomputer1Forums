from django.conf.urls import url

from . import views
from . import api_views

urlpatterns = [
    # /
    url(r'^$', views.forumlist, name='forumlist'),
    # /#/
    url(r'^(?P<forum_id>[0-9]+)/$', views.topiclist, name='topiclist'),
    # /newtopic/#/
    url(r'^newtopic/(?P<forum_id>[0-9]+)/$', views.newtopic, name='newtopic'),
    # /topic/#/
    url(r'^topic/(?P<topic_id>[0-9]+)/$', views.viewtopic, name='viewtopic'),
    # /topic/#/move_topic/
    url(r'^topic/(?P<topic_id>[0-9]+)/move_topic/$', views.movetopic, name='movetopic'),
    # /topic/#/open_close/[o,c]/
    url(r'^topic/(?P<topic_id>[0-9]+)/open_close/(?P<open_close>[oc])/$', views.openclosetopic, name='openclosetopic'),
    # /topic/#/delete/
    url(r'^topic/(?P<topic_id>[0-9]+)/delete/$', views.deletetopic, name='deletetopic'),
    # /post/#/
    url(r'^post/(?P<post_id>[0-9]+)/$', views.gotopost, name='gotopost'),
    # /post/#/edit/
    url(r'^post/(?P<post_id>[0-9]+)/edit/$', views.editpost, name='editpost'),
    # /post/#/move_post/
    url(r'^post/(?P<post_id>[0-9]+)/move_post/$', views.movepost, name='movepost'),
    # /post/#/delete/
    url(r'^post/(?P<post_id>[0-9]+)/delete/$', views.deletepost, name='deletepost'),
    # /user/*/
    url(r'^user/(?P<username>[a-zA-Z0-9\-_]+)/$', views.viewuser, name='viewuser'),
    # /user/*/manage_ban/
    url(r'^user/(?P<username>[a-zA-Z0-9\-_]+)/manage_ban/$', views.banuser, name='banuser'),
    # /account/register/
    url(r'^account/register/', views.registeraccount, name='registeraccount'),
    # /account/login/
    url(r'^account/login/', views.loginaccount, name='loginaccount'),
    # /account/change_password/
    url(r'^account/change_password/', views.changepassword, name='changepassword'),
    # /account/logout/
    url(r'^account/logout/', views.logouttask, name='logout'),
    # /action/report/#/
    url(r'^action/report/(?P<post_id>[0-9]+)/', views.report, name='postid'),
    # /settings/*/
    url(r'^settings/(?P<username>[a-zA-Z0-9\-_]+)/$', views.changesignature, name='changesignature'),
    # /banappeal/
    url(r'^banappeal/', views.banappeal, name='banappeal'),
    # /topic/#/rename_topic/
    url(r'topic/(?P<topic_id>[0-9]+)/rename_topic/$', views.renametopic, name='renametopic'),
    # /user/*/rank_change/
    url(r'^user/(?P<username>[a-zA-Z0-9\-_]+)/rank_change/$', views.changerank, name='changerank'),   
    # /_admin/
    url(r'^_admin/$', views.admin, name='admin'),
    # /topic/#/stick_unstick/[s,u]/
    url(r'^topic/(?P<topic_id>[0-9]+)/stick_unstick/(?P<stick_unstick>[su])/$', views.sticktopic, name='stickunstick'),
    # /account/delete_account/
    url(r'^account/delete_account/$', views.deleteaccount, name='deleteaccount'),
    # /account/account_deleted/
    url(r'^account/account_deleted/$', views.accountdeleted, name='accountdeleted'),
    # /user/*/delete/
    url(r'^user/(?P<username>[a-zA-Z0-9\-_]+)/delete/$', views.admindelete, name='admindelete'),
    # /post/#/source/
    url(r'^post/(?P<post_id>[0-9]+)/source/$', views.bbcodesource, name='source'),
    # /post/#/author/
    url(r'^post/(?P<post_id>[0-9]+)/author/$', views.postauthor, name='author'),
    # /post/#/json/
    url(r'^post/(?P<post_id>[0-9]+)/json/$', views.postasjson, name='postjson'),
    # /settings/*/details/
    url(r'^settings/(?P<username>[a-zA-Z0-9\-_]+)/details/$', views.settingsdetails, name='settingsdetails'),
    # /messages/
    url(r'^messages/$', views.messagesview, name='messages'),
    # /messages/delete_message/#/
    url(r'^messages/delete_messages/(?P<msg_id>[0-9]+)/$', views.deletemsg, name='deletemessage'),
    # /user/*/send_admin_message/
    url(r'^user/(?P<username>[a-zA-Z0-9\-_]+)/send_admin_message/$', views.sendmsg, name='sendmsg'),
    # /topic/#/followservice/
    url(r'^topic/(?P<topic_id>[0-9]+)/followservice/$', views.followunfollow, name='followunfollow'),
    # /user/*/admin_messages/
    url(r'^user/(?P<username>[a-zA-Z0-9\-_]+)/admin_messages/$', views.adminmessages),
    # /user/*/admin_messages/delete/#
    url(r'^user/(?P<username>[a-zA-Z0-9\-_]+)/admin_messages/delete/(?P<mid>[0-9]+)/$', views.deleteadminmsg),
    # /user/*/view_posts/
    url(r'^user/(?P<username>[a-zA-Z0-9\-_]+)/view_posts/$', views.viewposts),
    
    ####################
    ##### API      #####
    ####################
    #No Version

    # /api/ - API
    url(r'^api/$', api_views.api),

    ####
    #v1#
    ####
    
    # /api/v1/ - API Info
    url(r'^api/v1/$', api_views.v1),

    # /api/v1/info/ - Forum Info
    url(r'^api/v1/info/$', api_views.v1_info),

    # /api/v1/user/:user - Get a user
    url(r'^api/v1/user/(?P<username>[a-zA-Z0-9\-_]+)/$', api_views.v1_user_username),

    # /api/v1/post/:postid - Get a post
    url(r'^api/v1/post/(?P<post_id>[0-9]+)/$', api_views.v1_post),

    # /api/v1/topic/:topicid - Get a topic
    url(r'^api/v1/topic/(?P<topic_id>[0-9]+)/$', api_views.v1_topic),
]
