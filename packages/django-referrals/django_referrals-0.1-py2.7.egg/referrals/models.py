import uuid

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
        
    
class Referral(models.Model):
    user = models.OneToOneField(User, related_name="referral")
    unique_key = models.CharField(max_length=100)
    
    referred_users = models.ManyToManyField(User, blank=True, related_name="referrals")
        
    def __unicode__(self):
        return unicode(self.user)

    class Meta():
        verbose_name = 'referral'
        verbose_name_plural = 'referrals'

@receiver(post_save, sender=User)
def create_referral(sender, instance, created, **kwargs):
    """Create a matching referral whenever a user object is created."""
    referral, new = Referral.objects.get_or_create(user=instance, defaults={'unique_key': uuid.uuid1().hex})
