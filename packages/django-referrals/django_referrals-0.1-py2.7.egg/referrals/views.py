from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.conf import settings

from referrals.forms import RegistrationForm
from referrals.models import Referral

def refer(request, unique_key):
        
    referral = get_object_or_404(Referral, unique_key=unique_key)
    request.session['referral_id'] = referral.id

    return redirect(settings.REFERRAL_REDIRECT_URL)
