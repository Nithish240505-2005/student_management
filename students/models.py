from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Course(models.Model):
    """Model for academic courses"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        ordering = ['name']


class Student(models.Model):
    """Model for student records"""
    
    # Auto-generated student ID
    student_id = models.CharField(max_length=20, unique=True, editable=False)
    
    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    # Contact Information
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17)
    address = models.TextField(blank=True)
    
    # Academic Information
    date_of_birth = models.DateField()
    enrollment_date = models.DateField()
    course = models.ForeignKey(
        Course, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='students'
    )
    
    # Profile Photo
    profile_photo = models.ImageField(
        upload_to='student_photos/', 
        blank=True, 
        null=True
    )
    
    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
    ]
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True
    )
    
    def save(self, *args, **kwargs):
        """Override save to generate student ID"""
        if not self.student_id:
            self.student_id = self.generate_student_id()
        super().save(*args, **kwargs)
    
    def generate_student_id(self):
        """Generate unique student ID in format: STU{YEAR}{NUMBER}"""
        year = self.enrollment_date.year
        last_student = Student.objects.filter(
            student_id__startswith=f'STU{year}'
        ).order_by('student_id').last()
        
        if last_student:
            last_number = int(last_student.student_id[-4:])
            new_number = last_number + 1
        else:
            new_number = 1
        
        return f'STU{year}{new_number:04d}'
    
    @property
    def full_name(self):
        """Return full name of student"""
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"{self.student_id} - {self.full_name}"
    
    class Meta:
        ordering = ['-enrollment_date', 'last_name']