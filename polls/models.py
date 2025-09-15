from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_ROLE_CHOICES = (
        ("admin", "Admin"),
        ("student", "Student"),
    )
    role = models.CharField(max_length=10, choices=USER_ROLE_CHOICES, default="student")
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)

class Election(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates')
    full_name = models.CharField(max_length=200)
    bio = models.TextField(null=True, blank=True)
    vote_count = models.IntegerField(default=0)
    image = models.ImageField(upload_to='candidate_images/', null=True, blank=True)

    def __str__(self):
        return self.full_name

class CandidateField(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.candidate}: {self.name}"

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'election')

class VotingSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Voting session for {self.user.username}"