# app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import json

class User(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    hashed_password = models.CharField(max_length=255)
    points = models.IntegerField(default=0)
    is_admin = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username

class Course(models.Model):
    yaml_id = models.CharField(max_length=50, unique=True)  # e.g., "en_pe_course"
    title = models.CharField(max_length=200)
    points = models.IntegerField(default=0)
    badge = models.CharField(max_length=255, null=True, blank=True)  # Nullable for badges
    short_description = models.TextField(blank=True, default='')  # Empty string for existing rows
    version = models.CharField(max_length=10, default='0.0.0')  # Default version
    duration = models.CharField(max_length=50, default='Unknown')  # Default duration
    difficulty = models.CharField(max_length=50, default='Unknown')  # Default difficulty
    language = models.CharField(max_length=50, default='English')  # Default language
    course_type = models.CharField(max_length=50, default='Unknown')  # Default course type
    level = models.CharField(max_length=10, default='0')  # Default level
    topics = models.JSONField(default=dict)  # Empty dict for topics
    overview = models.TextField(blank=True, default='')  # Empty string for overview

    class Meta:
        db_table = 'courses'

    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    yaml_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    points = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'modules'

    def __str__(self):
        return self.title

class Section(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='sections')
    yaml_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    content = models.TextField()  # Base64-encoded markdown
    points = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'sections'

    def __str__(self):
        return self.title

class Exercise(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='exercises')
    content = models.TextField()  # Base64-encoded markdown
    points = models.IntegerField(default=0)

    class Meta:
        db_table = 'exercises'

    def __str__(self):
        return f"Exercise for {self.module.title}"

class Completion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=20)  # 'course', 'module', 'section', 'exercise'
    item_id = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)
    points_earned = models.IntegerField(default=0)

    class Meta:
        db_table = 'completions'

    def __str__(self):
        return f"{self.user.username} - {self.item_type} {self.item_id}"