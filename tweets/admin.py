from django.contrib import admin
from tweets.models import Tweet


@admin.register(Tweet)
# inherit from admin.ModelAdmin
class TweetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at' #filtered by 'created_at'
    list_display = (
        'created_at',
        'user',
        'content',
    )