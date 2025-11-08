from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Static pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/intern/<str:username>/', views.intern_profile_public_view, name='intern_profile_public'),
    
    # Document Management
    path('profile/document/upload/', views.document_upload_view, name='document_upload'),
    path('profile/document/<int:document_id>/delete/', views.document_delete_view, name='document_delete'),
    
    # Education Management
    path('profile/education/add/', views.education_create_view, name='education_add'),
    path('profile/education/<int:education_id>/edit/', views.education_update_view, name='education_edit'),
    path('profile/education/<int:education_id>/delete/', views.education_delete_view, name='education_delete'),
    
    # Work Experience Management
    path('profile/experience/add/', views.work_experience_create_view, name='experience_add'),
    path('profile/experience/<int:experience_id>/edit/', views.work_experience_update_view, name='experience_edit'),
    path('profile/experience/<int:experience_id>/delete/', views.work_experience_delete_view, name='experience_delete'),
    
    # Explore
    path('explore/', views.explore, name='explore'),
    
    # Messages
    path('messages/', views.messages_list, name='messages'),
    path('messages/<int:conversation_id>/', views.conversation_detail_view, name='conversation_detail'),
    path('messages/start/<str:intern_username>/', views.start_conversation_view, name='start_conversation'),
    
    # Internships
    path('internships/', views.internship_list_view, name='internship_list'),
    path('internships/<int:pk>/', views.internship_detail_view, name='internship_detail'),
    path('internships/create/', views.internship_create_view, name='internship_create'),
    path('internships/<int:pk>/edit/', views.internship_update_view, name='internship_edit'),
    path('internships/<int:pk>/delete/', views.internship_delete_view, name='internship_delete'),
    path('my-internships/', views.employer_internships_view, name='employer_internships'),
]
