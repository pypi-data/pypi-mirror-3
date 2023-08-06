from django.contrib import admin
from omblog.models import Tag, Post
from omblog.forms import PostForm
from omblog.models import PostVersion


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = ({'slug' : ('tag',)})
    fieldsets = (
        (None, {
            'fields': ('tag',
                        'slug')
        }),
    )


class PostVersionAdmin(admin.ModelAdmin):
    pass


class PostAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    form = PostForm
    prepopulated_fields = ({'slug' : ('title',)})
    list_display = ['title', 'description', 'created']
    search_fields = ['title', 'description']
    list_filter = ['status']
    filter_horizontal = ['tags']
    fieldsets = (
        (None, {
            'classes': ('content',),
            'fields': ('title',
                        'description',
                        'source_content',
                        'tags',
                        'status')
        }),
        ('Misc', {
            'classes': ('collapse',),
            'fields': ('slug',
                        'rendered_content',
                        'created')
        }),
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostVersion, PostVersionAdmin)
