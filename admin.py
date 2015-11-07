from django.contrib import admin

from .models import *

# Register your models here.
class PostInline(admin.StackedInline):
    model = Post
    extra = 1

class ForumUserAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': [
            'username', 'ban_message', 'signature', 'user', 'rank'
        ]}),
    ]

class SectionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': [
            'name', 'location'
        ]}),
    ]

class ForumAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': [
            'section', 'location', 'name', 'info', 'latest_post_id', 'latest_poster'
        ]}),
    ]

class TopicAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': [
            'forum', 'name', 'posted_by', 'latest_post_id', 'latest_poster',
            'closed', 'post_date', 'sticky', 'last_post_date',
        ]}),
    ]
    inlines = [PostInline]

class ReportAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': [
            'reporter', 'reported', 'report_message', 'report_status', 'report_date'
        ]}),
    ]

admin.site.register(ForumUser, ForumUserAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Report, ReportAdmin)
