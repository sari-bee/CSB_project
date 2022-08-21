from django.db import models

# Create your models here.

class User(models.Model):
    username = models.CharField(max_length=200, unique=True)
    password = models.CharField(max_length=200)
    def __str__(self):
        return self.username

class Task(models.Model):
    task_text = models.CharField(max_length=200)
    task_user = models.ForeignKey(User, on_delete=models.CASCADE)
    done = models.IntegerField(default=0)
    task_number = models.IntegerField(default=0, unique=True)
    def __str__(self):
        return self.task_text