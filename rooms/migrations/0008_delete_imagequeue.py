from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0007_room_mode_youtube_only"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ImageQueue",
        ),
    ]
