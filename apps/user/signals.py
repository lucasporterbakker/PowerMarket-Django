from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from apps.manager.models import Project
from .models import UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create UserProfile when User model is created.
    This is important because the user forwarding
    will fail if no profile exists.
    """
    if created:
        profile = UserProfile(user=instance)
        profile.save()
        project = Project(profile=profile)
        project.save()
