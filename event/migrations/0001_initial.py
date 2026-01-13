from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("bd_models", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the event",
                        max_length=128,
                        unique=True,
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, help_text="Description of the event"),
                ),
                (
                    "enabled",
                    models.BooleanField(
                        default=True, help_text="Whether this event is visible to players"
                    ),
                ),
                (
                    "is_permanent",
                    models.BooleanField(
                        default=False,
                        help_text="If True, this is a permanent event. If False, use start_date and end_date.",
                    ),
                ),
                (
                    "start_date",
                    models.DateTimeField(
                        blank=True,
                        help_text="Start date for limited-time events. Ignored if is_permanent=True.",
                        null=True,
                    ),
                ),
                (
                    "end_date",
                    models.DateTimeField(
                        blank=True,
                        help_text="End date for limited-time events. Ignored if is_permanent=True.",
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Event",
                "verbose_name_plural": "Events",
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="EventIncludedBalls",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "ball",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bd_models.ball",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="event.event",
                    ),
                ),
            ],
            options={
                "verbose_name": "Event Included Ball",
                "verbose_name_plural": "Event Included Balls",
            },
        ),
        migrations.CreateModel(
            name="EventImportantBalls",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "ball",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="bd_models.ball",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="event.event",
                    ),
                ),
            ],
            options={
                "verbose_name": "Event Important Ball",
                "verbose_name_plural": "Event Important Balls",
            },
        ),
        migrations.AddField(
            model_name="event",
            name="included_balls",
            field=models.ManyToManyField(
                blank=True,
                help_text="All balls included in this event",
                related_name="events",
                to="bd_models.ball",
            ),
        ),
        migrations.AddField(
            model_name="event",
            name="important_balls",
            field=models.ManyToManyField(
                blank=True,
                help_text="Featured or important balls in this event (subset of included_balls)",
                related_name="important_events",
                to="bd_models.ball",
            ),
        ),
    ]
