from django.dispatch import Signal

#sender is the referral, instance is the user
sign_up = Signal(providing_args=["instance"])
