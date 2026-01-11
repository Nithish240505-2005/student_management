from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('', views.index_view, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Student URLs
    path('students/', views.student_list_view, name='student_list'),
    path('students/add/', views.student_create_view, name='student_create'),
    path('students/<int:pk>/', views.student_detail_view, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_update_view, name='student_update'),
    path('students/<int:pk>/delete/', views.student_delete_view, name='student_delete'),
    path('students/export/', views.export_students_csv, name='export_students'),
    
    # Course URLs
    path('courses/', views.course_list_view, name='course_list'),
    path('courses/add/', views.course_create_view, name='course_create'),
]