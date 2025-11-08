from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    # Application submission
    path('apply/<int:internship_id>/', views.application_create_view, name='create'),
    
    # Application management
    path('<int:pk>/', views.application_detail_view, name='detail'),
    path('my-applications/', views.application_list_view, name='list'),
    
    # Employer views
    path('<int:pk>/update-status/', views.application_update_status_view, name='update_status'),
    path('internship/<int:internship_id>/', views.internship_applications_view, name='internship_applications'),
]

