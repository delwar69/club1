from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        user = self.create_user(email, first_name, last_name, password)
        user.is_admin = True
        user.is_staff = True  # Superusers must be staff
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)  # Corrected default=True
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)  # Added is_staff field

    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email  

    @property
    def is_superuser(self):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        """Allow admin users to have all permissions."""
        return self.is_admin

    def has_module_perms(self, app_label):
        """Allow admin users to view all app modules."""
        return self.is_admin
