from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0006_remove_coursenote_rooms_cours_room_id_c014f5_idx_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="room",
            name="mode",
            field=models.CharField(choices=[("youtube", "YouTube")], default="youtube", max_length=10),
        ),
    ]
