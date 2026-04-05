from django.conf import settings
from django.db import migrations, models


def create_missing_profiles(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL.split(".")[0], settings.AUTH_USER_MODEL.split(".")[1])
    UserProfile = apps.get_model("authentification", "UserProfile")

    existing_user_ids = set(UserProfile.objects.values_list("user_id", flat=True))
    missing_profiles = [
        UserProfile(user_id=user.id)
        for user in User.objects.all().only("id")
        if user.id not in existing_user_ids
    ]
    if missing_profiles:
        UserProfile.objects.bulk_create(missing_profiles)


class Migration(migrations.Migration):

    dependencies = [
        ("authentification", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="role",
            field=models.CharField(
                choices=[("teacher", "Professeur"), ("student", "Eleve")],
                default="student",
                max_length=20,
            ),
        ),
        migrations.RunPython(create_missing_profiles, migrations.RunPython.noop),
    ]
