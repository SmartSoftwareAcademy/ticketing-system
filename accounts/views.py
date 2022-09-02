from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.db.models.query_utils import Q
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from . forms import SignUpForm

from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from ticketapp.views import send_email

# Create your views here.
def home(request):
    return redirect('ticketapp:ticket-list')

def user_login(request):
    '''Log the user into the system'''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('ticketapp:ticket-list')
        else:
            messages.error(request, 'Invalid Login Credentials')

    return render(request, 'accounts/login.html')


def user_logout(request):
    logout(request)
    return redirect('/')


def signup(request):
    if request.method == 'POST':

        form = SignUpForm(request.POST)
        raw_password = request.POST['password1']
        password2 = request.POST['password2']

        if raw_password != password2:
            messages.error(request, 'Passwords do not match')
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            raw_password = form.cleaned_data['password1']

            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')

    else:
        form = SignUpForm()
    return render(request, 'accounts/register.html', {'form': form})


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            domain = request.META['HTTP_HOST']
            protocol = 'https' if request.is_secure() else 'http'
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "accounts/reset_email.txt"
                    c = {
                        "email": user.email,
                        'domain': domain,
                        'site_name': 'Helpdesk',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': protocol,
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_email(request, subject, email, [user.email], [])
                        print("Reset email sent!")
                    except Exception as e:
                        return HttpResponse('Invalid header found:{}'.format(e))
                    return redirect("accounts:reset_done")
    else:
        password_reset_form = PasswordResetForm()
    return render(request=request, template_name="accounts/forgot-password.html", context={"password_reset_form": password_reset_form})
