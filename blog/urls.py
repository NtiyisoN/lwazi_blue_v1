from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.blog_list, name='list'),
    path('<slug:slug>/', views.blog_detail, name='detail'),
    path('create/', views.blog_create, name='create'),
    path('<slug:slug>/edit/', views.blog_edit, name='edit'),
]

