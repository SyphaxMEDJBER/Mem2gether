from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0003_remove_room_youtube_is_playing_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="room",
            name="youtube_state",
            field=models.CharField(blank=True, default="paused", max_length=10),
        ),
        migrations.AddField(
            model_name="room",
            name="youtube_time",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="room",
            name="youtube_updated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
