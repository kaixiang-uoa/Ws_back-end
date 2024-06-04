from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings
from taggit.managers import TaggableManager


class UserType(models.Model):
    type_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.type_name

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)  # Use set_password to hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', UserType.objects.get(type_name='Admin'))
        return self.create_user(username, email, password, **extra_fields)

class Ws_User(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    user_type = models.ForeignKey(UserType, on_delete=models.CASCADE, null=True)
    is_approved = models.BooleanField(default=False)  
    needs_review = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)
    avatar_path = models.ImageField(upload_to='avatars/', blank=True, null=True)
    documents = models.FileField(upload_to='documents/', blank=True, null=True) 
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

class UserRelation(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class ProfessorAvailability(models.Model):
    professor = models.ForeignKey(Ws_User, on_delete=models.CASCADE, related_name='availability_set')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.professor.username} - {self.start_time} to {self.end_time}"
    
# class UserImage(models.Model):
#     user = models.ForeignKey(Ws_User, on_delete=models.CASCADE)
#     image = models.ImageField(upload_to='user_images/')

#     def __str__(self):
#         return f"{self.user.username} Image"

