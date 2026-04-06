from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0008_delete_imagequeue"),
    ]

    operations = [
        migrations.AddField(
            model_name="room",
            name="whiteboard_data",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="room",
            name="whiteboard_updated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
