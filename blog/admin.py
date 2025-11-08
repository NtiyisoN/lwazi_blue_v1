from django.contrib import admin
from .models import BlogPost, BlogCategory, BlogTag


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'published_at', 'views_count']
    list_filter = ['is_published', 'category', 'published_at', 'created_at']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['views_count', 'created_at', 'updated_at', 'published_at']
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('Post Details', {
            'fields': ('title', 'slug', 'author', 'category', 'tags')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('Publishing', {
            'fields': ('is_published', 'published_at', 'views_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publish_posts', 'unpublish_posts']
    
    def publish_posts(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(is_published=False).update(is_published=True, published_at=timezone.now())
        self.message_user(request, f'{updated} post(s) published.')
    publish_posts.short_description = 'Publish selected posts'
    
    def unpublish_posts(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} post(s) unpublished.')
    unpublish_posts.short_description = 'Unpublish selected posts'
