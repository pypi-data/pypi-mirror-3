from referrals.models import Referral
from referrals.signals import sign_up

def process_request(request, new_user):
    "If there is a referring user, add the new_user to it's referrals"

    if 'referral_id' in request.session:
        referral = Referral.objects.get(id=request.session['referral_id'])
        referral.referred_users.add(new_user)
        
        #send off the signal
        sign_up.send(sender=referral, instance=new_user)
