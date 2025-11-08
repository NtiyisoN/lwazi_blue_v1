from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import BlogPost, BlogCategory, BlogTag


def blog_list(request):
    """List all published blog posts"""
    posts = BlogPost.objects.filter(is_published=True).select_related('author', 'category')
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Filter by tag
    tag_slug = request.GET.get('tag')
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    
    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories and tags for sidebar
    categories = BlogCategory.objects.all()
    tags = BlogTag.objects.all()
    
    context = {
        'posts': page_obj,
        'categories': categories,
        'tags': tags,
        'current_category': category_slug,
        'current_tag': tag_slug,
    }
    
    return render(request, 'blog/blog_list.html', context)


def blog_detail(request, slug):
    """View single blog post"""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Increment views
    post.increment_views()
    
    # Get related posts
    related_posts = BlogPost.objects.filter(
        is_published=True,
        category=post.category
    ).exclude(pk=post.pk)[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    
    return render(request, 'blog/blog_detail.html', context)


@login_required
def blog_create(request):
    """Create new blog post - admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only admins can create blog posts.')
        return redirect('blog:list')
    
    messages.info(request, 'Blog creation will be done via Django admin for now.')
    return redirect('/admin/blog/blogpost/add/')


@login_required
def blog_edit(request, slug):
    """Edit blog post - admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only admins can edit blog posts.')
        return redirect('blog:list')
    
    post = get_object_or_404(BlogPost, slug=slug)
    messages.info(request, 'Blog editing will be done via Django admin for now.')
    return redirect(f'/admin/blog/blogpost/{post.pk}/change/')
