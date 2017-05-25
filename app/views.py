from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AdminPasswordChangeForm, PasswordChangeForm
from django.contrib.auth import login, update_session_auth_hash
from django.contrib import messages

from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from social_core.pipeline import user

from social_django.models import UserSocialAuth

from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .tokens import account_activation_token
from .forms import RegistrationForm, AdditionalForm
from django.contrib.auth.models import User


def index(request):
    return render(request, 'app/index.html')

def cameras(request):
    return render(request, 'app/cameras.html')

def team(request):
    return render(request, 'app/team.html')

def privacy(request):
    return render(request, 'app/privacy.html')

def terms(request):
    return render(request, 'app/terms.html')

def acknowledgement(request):
    return render(request, 'app/ack.html')

def contact(request):
    return render(request, 'app/contact.html')

def faqs(request):
    return render(request, 'app/faq.html')

def register(request):
    if request.method == 'POST':
        form1 = RegistrationForm(request.POST)
        form2 = AdditionalForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            model1 = form1.save(commit=False)
            model1.is_active = False
            model1.save()
            model2 = form2.save(commit=False)
            model2.user = model1
            model2.save()
            current_site = get_current_site(request)
            subject = 'Activate Your MySite Account'
            message = render_to_string('app/confirmation_email.html', {
                'user': model1,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(model1.pk)),
                'token': account_activation_token.make_token(model1),
            })
            model1.email_user(subject, message)
            return redirect('email_confirmation_sent')
    else:
        form1 = RegistrationForm()
        form2 = AdditionalForm()
    return render(request, 'app/register.html', {'form1': form1, 'form2': form2})

def email_confirmation_sent(request):
    return render(request, 'app/email_confirmation_sent.html')

def email_confirmation_invalid(request):
    return render(request, 'app/email_confirmation_invalid.html')

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.registeruser.email_confirmed = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'email_confirmation_invalid.html')


def faqs(request):
    return render(request, 'app/faq.html')

@login_required
def profile(request):
    user = request.user

    try:
        github_login = user.social_auth.get(provider='github')
    except UserSocialAuth.DoesNotExist:
        github_login = None
    if github_login:        
        return render(request, 'app/profile.html', {
            'github_login': github_login,
        })
    else:
        return redirect('index')

@login_required
def password(request):
    return render(request, 'app/password.html', {'form': form})