from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager,Group,Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

#custom user manager
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **external_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **external_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **external_fields):
        external_fields.setdefault('is_staff', True)
        external_fields.setdefault('is_superuser', True)
        external_fields.setdefault('is_activate', True)
        return self.create_user(email,password,**external_fields)
    
#custom user model
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)
    position = models.CharField(max_length=200, blank=True, null=True)
    is_activate = models.BooleanField(default=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =[]

    def __str__(self):
        return self.email
    
#profile model
class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20,blank=True,null=True)
    profile_picture = models.ImageField(upload_to='profile/', null=True,blank=True)
    address = models.TextField(null=True,blank=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"
    
# signal
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    instance.profile.save()