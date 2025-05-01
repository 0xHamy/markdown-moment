# app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

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
    id = models.IntegerField(primary_key=True)
    yaml_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    points = models.IntegerField(default=0)
    creator_info = models.TextField()

    class Meta:
        db_table = 'courses'

    def __str__(self):
        return self.title

class Module(models.Model):
    id = models.IntegerField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    yaml_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    points = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'modules'

    def __str__(self):
        return self.title

class Section(models.Model):
    id = models.IntegerField(primary_key=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='sections')
    yaml_id = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    content = models.TextField()
    points = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'sections'

    def __str__(self):
        return self.title

class Exercise(models.Model):
    id = models.IntegerField(primary_key=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='exercise')
    content = models.TextField()
    points = models.IntegerField(default=0)

    class Meta:
        db_table = 'exercises'

    def __str__(self):
        return f"Exercise for {self.module.title}"

class Completion(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=20)
    item_id = models.IntegerField()

    class Meta:
        db_table = 'completions'

    def __str__(self):
        return f"{self.user.username} - {self.item_type} {self.item_id}"

