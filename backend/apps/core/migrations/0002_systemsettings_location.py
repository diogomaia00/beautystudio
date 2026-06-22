from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemsettings",
            name="location",
            field=models.CharField(
                blank=True,
                default="Rua Vila Vieira 17, Ançã",
                max_length=255,
            ),
        ),
    ]
