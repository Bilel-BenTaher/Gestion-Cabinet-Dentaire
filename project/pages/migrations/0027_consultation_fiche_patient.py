# Generated by Django 5.1.3 on 2024-12-31 19:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0026_remove_facture_date_facture_id_patient'),
    ]

    operations = [
        migrations.AddField(
            model_name='consultation',
            name='fiche_patient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cons_fich', to='pages.fichepatient'),
        ),
    ]