from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("event", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="image_url",
            field=models.URLField(
                blank=True,
                help_text="URL to an image for this event (displayed in the embed)",
                null=True,
            ),
        ),
    ]
