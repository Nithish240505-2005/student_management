from django.contrib import admin
from .models import Student, Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Admin interface for Course model"""
    list_display = ['code', 'name', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['created_at']
    ordering = ['name']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model"""
    list_display = [
        'student_id', 'first_name', 'last_name', 
        'email', 'course', 'status', 'enrollment_date'
    ]
    list_filter = ['status', 'course', 'enrollment_date']
    search_fields = ['student_id', 'first_name', 'last_name', 'email']
    readonly_fields = ['student_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'profile_photo')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number', 'address')
        }),
        ('Academic Information', {
            'fields': ('student_id', 'course', 'enrollment_date', 'status')
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set created_by when creating new student"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)