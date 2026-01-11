from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
import csv
from datetime import datetime

from .models import Student, Course
from .forms import StudentForm, UserRegistrationForm, CourseForm


# Authentication Views
def index_view(request):
    """Landing page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'students/index.html')


def register_view(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'students/register.html', {'form': form})


def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'students/login.html')


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


# Dashboard View
@login_required
def dashboard_view(request):
    """Display dashboard with statistics"""
    total_students = Student.objects.count()
    active_students = Student.objects.filter(status='active').count()
    total_courses = Course.objects.count()
    
    students_by_course = Course.objects.annotate(
        student_count=Count('students')
    ).order_by('-student_count')[:5]
    
    recent_students = Student.objects.all()[:5]
    
    context = {
        'total_students': total_students,
        'active_students': active_students,
        'total_courses': total_courses,
        'students_by_course': students_by_course,
        'recent_students': recent_students,
    }
    return render(request, 'students/dashboard.html', context)


# Student CRUD Views
@login_required
def student_list_view(request):
    """Display list of students with search and filter"""
    students = Student.objects.select_related('course').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filter by course
    course_filter = request.GET.get('course', '')
    if course_filter:
        students = students.filter(course_id=course_filter)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        students = students.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    courses = Course.objects.all()
    
    context = {
        'page_obj': page_obj,
        'courses': courses,
        'search_query': search_query,
        'course_filter': course_filter,
        'status_filter': status_filter,
    }
    return render(request, 'students/student_list.html', context)


@login_required
def student_detail_view(request, pk):
    """Display detailed view of a student"""
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'students/student_detail.html', {'student': student})


@login_required
def student_create_view(request):
    """Create a new student"""
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            student = form.save(commit=False)
            student.created_by = request.user
            student.save()
            messages.success(request, f'Student {student.full_name} added successfully!')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm()
    return render(request, 'students/student_form.html', {
        'form': form, 
        'action': 'Add'
    })


@login_required
def student_update_view(request, pk):
    """Update an existing student"""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Student {student.full_name} updated successfully!')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/student_form.html', {
        'form': form, 
        'action': 'Edit', 
        'student': student
    })


@login_required
def student_delete_view(request, pk):
    """Delete a student"""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student_name = student.full_name
        student.delete()
        messages.success(request, f'Student {student_name} deleted successfully!')
        return redirect('student_list')
    return render(request, 'students/student_confirm_delete.html', {
        'student': student
    })


# Export View
@login_required
def export_students_csv(request):
    """Export students data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="students_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Student ID', 'First Name', 'Last Name', 'Email', 'Phone',
        'Date of Birth', 'Enrollment Date', 'Course', 'Status'
    ])
    
    students = Student.objects.select_related('course').all()
    for student in students:
        writer.writerow([
            student.student_id,
            student.first_name,
            student.last_name,
            student.email,
            student.phone_number,
            student.date_of_birth,
            student.enrollment_date,
            student.course.name if student.course else '',
            student.get_status_display()
        ])
    
    return response


# Course Views
@login_required
def course_list_view(request):
    """Display list of courses"""
    courses = Course.objects.annotate(
        student_count=Count('students')
    ).all()
    return render(request, 'students/course_list.html', {'courses': courses})


@login_required
def course_create_view(request):
    """Create a new course"""
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            messages.success(request, f'Course {course.name} created successfully!')
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'students/course_form.html', {
        'form': form, 
        'action': 'Add'
    })