# Generated by Django 5.1.3 on 2024-12-19 19:41

import django.db.models.deletion
import phonenumber_field.modelfields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CabinetDentaire',
            fields=[
                ('id_cabinet', models.AutoField(primary_key=True, serialize=False)),
                ('intitule', models.CharField(max_length=254)),
                ('address', models.CharField(max_length=254)),
                ('email', models.EmailField(max_length=254)),
                ('tel', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('fax', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
            ],
        ),
        migrations.CreateModel(
            name='Facture',
            fields=[
                ('id_facture', models.AutoField(primary_key=True, serialize=False)),
                ('prix', models.FloatField()),
                ('date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Ordonnance',
            fields=[
                ('id_ordonnance', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('medicament', models.CharField(max_length=254)),
                ('observation', models.CharField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Consultation',
            fields=[
                ('id_consultation', models.AutoField(primary_key=True, serialize=False)),
                ('contenue', models.TextField(max_length=254)),
                ('antecedant', models.CharField(max_length=254)),
                ('traitement', models.CharField(max_length=254)),
                ('date_consultation', models.DateTimeField()),
                ('id_medecin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cons_medecine', to=settings.AUTH_USER_MODEL)),
                ('id_patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cons_patient', to=settings.AUTH_USER_MODEL)),
                ('id_facture', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cons_fact', to='pages.facture')),
            ],
        ),
        migrations.CreateModel(
            name='FichePatient',
            fields=[
                ('id_fiche', models.AutoField(primary_key=True, serialize=False)),
                ('nom', models.CharField(max_length=254)),
                ('prenom', models.CharField(max_length=254)),
                ('address', models.CharField(max_length=254)),
                ('age', models.IntegerField()),
                ('sexe', models.CharField(max_length=254)),
                ('tel', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('email', models.EmailField(max_length=254)),
                ('CNAM', models.CharField(max_length=254)),
                ('profession', models.CharField(max_length=254)),
                ('motif_consultation', models.CharField(max_length=254)),
                ('id_patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fich_patient', to=settings.AUTH_USER_MODEL)),
                ('id_secretaire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fich_sec', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rdv',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('num_rdv', models.IntegerField(default='1')),
                ('id_patient', models.ForeignKey(default='4', on_delete=django.db.models.deletion.CASCADE, related_name='rdv_patient', to=settings.AUTH_USER_MODEL)),
                ('id_secretaire', models.ForeignKey(default='3', on_delete=django.db.models.deletion.CASCADE, related_name='rdv_sec', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]