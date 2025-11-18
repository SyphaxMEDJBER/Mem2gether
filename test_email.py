import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from django.core.mail import send_mail

send_mail(
    'Test Django',
    'Ceci est un test.',
    'alaouisalma2002@gmail.com',  # From
    ['alaouisalma2002@gmail.com'],  # To
    fail_silently=False,
)
