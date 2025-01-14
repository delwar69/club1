from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, UserProfile

# Signal to create or get a UserProfile when a new user is created
@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create the UserProfile only if it does not already exist
        UserProfile.objects.get_or_create(user=instance)
