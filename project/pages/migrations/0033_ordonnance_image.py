# Generated by Django 5.1.3 on 2025-01-01 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0032_alter_ordonnance_id_patient'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordonnance',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='ordonnances/'),
        ),
    ]