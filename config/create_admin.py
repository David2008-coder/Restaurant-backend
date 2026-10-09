import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if not all([email, username, password]):
    raise RuntimeError("Admin environment variables are missing.")

user = User.objects.filter(email=email).first()

if user is None:
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        role="admin",
    )
else:
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.role = "admin"
    user.save()

print("Admin account recovery completed.")
