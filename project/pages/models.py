# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.
# class Medecin (Utilisateur):
# 	    id_medecin = models.AutoField(primary_key=True)
# 		id_utilisateur = models.ForeignKey('Utilisateur',on_delete=models.CASCADE)
		
# class Administrateur (Utilisateur):
# 	    id_admin = models.AutoField(primary_key=True)
# 		id_utilisateur = models.ForeignKey('Utilisateur',on_delete=models.CASCADE,)
		
# class Secretaire (Utilisateur):
# 	    id_secretaire = models.AutoField(primary_key=True)
# 		id_utilisateur = models.ForeignKey('Utilisateur',on_delete=models.CASCADE, )
			

# class Patient (Utilisateur):
# 		id_patient = models.AutoField(primary_key=True)	
# 		id_utilisateur = models.ForeignKey('Utilisateur',on_delete=models.CASCADE, )
# 		id_cabinet = models.ForeignKey('CabinetDentaire',on_delete=models.CASCADE, )
# 		id_rdv = models.ForeignKey('Rdv',on_delete=models.CASCADE, )

# class Utilisateur (models.Model):
# 	id_utilisateur = models.AutoField(primary_key=True)
# 	login = models.CharField(max_length=254)
# 	password = models.CharField(max_length=254)
# 	nom = models.CharField(max_length=254)
# 	prenom = models.CharField(max_length=254)
# 	tel = PhoneNumberField(blank=True)
# 	address = models.CharField(max_length=254)
# 	email 	= models.EmailField()
# 	#role = models.CharField(default='utilisateur',max_length=254)
# 	def __str__ (self):
# 		return str(self.login)

## full_name = '%s %s' % (self.first_name, self.last_name)
## return full_name.strip()
class CabinetDentaire (models.Model):
		id_cabinet = models.AutoField(primary_key=True)
		intitule = models.CharField(max_length=254)
		address = models.CharField(max_length=254)
		email= models.EmailField()
		tel = PhoneNumberField(blank=True)
		fax =  PhoneNumberField(blank=True)
		def __str__ (self):
		 return str(self.intitule)

from datetime import timedelta
from datetime import datetime

class Rdv(models.Model):
    id = models.AutoField(primary_key=True)
    id_patient = models.ForeignKey(User, related_name="rdv_patient", on_delete=models.CASCADE, null=True, blank=True)
    fiche = models.ForeignKey('FichePatient', related_name="cons_fact", on_delete=models.CASCADE, null=True, blank=True)
    
    date = models.DateField()  # On utilise uniquement la date ici
    time = models.TimeField(null=True, blank=True)  # Pour stocker l'heure calculée
    num_rdv = models.IntegerField(default=1)  # Position dans la journée

    def calculate_time(self):
        """Calcule l'heure du rendez-vous en fonction du numéro et de la plage horaire."""
        start_morning = timedelta(hours=9)
        start_afternoon = timedelta(hours=14)
        consultation_duration = timedelta(minutes=35)

        # Calculer le temps total écoulé depuis le début de la journée
        total_time = (self.num_rdv - 1) * consultation_duration

        # Ajouter le temps calculé à la bonne plage horaire
        if total_time < timedelta(hours=4):  # Matin (9h-13h)
            appointment_time = start_morning + total_time
        else:  # Après-midi (14h-18h)
            appointment_time = start_afternoon + (total_time - timedelta(hours=4))

        return (datetime.min + appointment_time).time()  # Retourner un objet time

    def save(self, *args, **kwargs):
        if not self.time:
            self.time = self.calculate_time()  # Calculer l'heure automatiquement
        
        # Assignation automatique de la fiche patient basée sur l'id_patient
        if self.id_patient and not self.fiche:
            try:
                self.fiche = FichePatient.objects.get(id_patient=self.id_patient)
            except FichePatient.DoesNotExist:
                pass  # Si la fiche n'existe pas, on garde id_fiche à None (ou vous pouvez gérer autrement)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id_patient} - {self.date} à {self.time}"


from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

class FichePatient(models.Model):
    id_fiche = models.AutoField(primary_key=True)
    id_patient = models.ForeignKey(User, related_name="fich_patient", on_delete=models.CASCADE)
    nom = models.CharField(max_length=254)
    prenom = models.CharField(max_length=254)
    age = models.IntegerField()
    sexe = models.CharField(max_length=254)
    tel = PhoneNumberField(blank=True)
    motif_consultation = models.CharField(max_length=254)
    valide = models.BooleanField(default=False)  # Champ pour valider la fiche

    def __str__(self):
        return f"Fiche du Patient {self.id_patient.username}"

# Signal pour créer une consultation automatiquement après la validation d'une fiche
@receiver(post_save, sender=FichePatient)
def create_consultation(sender, instance, created, **kwargs):
    if instance.valide:  # Si la fiche est validée
        # Créer une consultation seulement si elle n'existe pas déjà
        if not hasattr(instance, 'consultation'):  # Si aucune consultation associée n'existe
            Consultation.objects.create(
                id_patient=instance.id_patient,
                # Remplir d'autres champs nécessaires, par exemple contenue ou traitement
                Observation="Consultation ",
                date_consultation=now().date(),  # Utiliser la date actuelle
            )
            # Rendre la fiche invalide après la création de la consultation
            instance.valide = False
            instance.save()


from django.utils import timezone  # Ajoutez cet import en haut de votre fichier

class Consultation(models.Model):
    id_consultation = models.AutoField(primary_key=True)
    id_patient = models.ForeignKey(User, related_name="cons_patient", on_delete=models.CASCADE)
    fiche_patient = models.ForeignKey('FichePatient', related_name="consultations", on_delete=models.CASCADE, null=True, blank=True)
    facture = models.ForeignKey('Facture', related_name="cons_fact", on_delete=models.CASCADE, null=True, blank=True)
    Observation = models.TextField(max_length=254)
    Traitement = models.ForeignKey('Ordonnance', related_name="cons_ord", on_delete=models.CASCADE, null=True, blank=True)
    date_consultation = models.DateField()
    valide = models.BooleanField(default=False)

    def __str__(self):
        return f"- Patient: {self.id_patient.username}"

    def save(self, *args, **kwargs):
        # Assigner automatiquement fiche_patient si non défini
        if not self.fiche_patient:
            try:
                self.fiche_patient = FichePatient.objects.get(id_patient=self.id_patient)
            except FichePatient.DoesNotExist:
                pass  # Gérer l'absence de FichePatient si nécessaire

        # Vérifier si une facture existe pour le patient ; sinon, la créer
        if not self.facture:
            try:
                self.facture = Facture.objects.get(id_patient=self.id_patient)
            except Facture.DoesNotExist:
                self.facture = Facture.objects.create(id_patient=self.id_patient, prix=0)  # Exemple : montant initial à 0

        # Vérifier si une ordonnance existe pour le patient ; sinon, la créer
        if not self.Traitement:
            try:
                self.Traitement = Ordonnance.objects.get(id_patient=self.id_patient)
            except Ordonnance.DoesNotExist:
                self.Traitement = Ordonnance.objects.create(
                    id_patient=self.id_patient,
                    date=now().date(),
                    medicament="Aucun traitement prescrit"  # Valeur par défaut pour le champ 'medicament'
                )

        super().save(*args, **kwargs)


class Facture (models.Model):
	id_facture = models.AutoField(primary_key=True)
	id_patient = models.ForeignKey(User, related_name="factures", on_delete=models.CASCADE, null=True)
	prix = models.FloatField()
	def __str__(self):
		return f"Facture du Patient {self.id_patient.username}"
     

class Ordonnance (models.Model):
	id_ordonnance = models.AutoField(primary_key=True)
	id_patient = models.ForeignKey(User, related_name="Ordonnance", on_delete=models.CASCADE, null=True)
	date = models.DateTimeField()
	medicament = models.CharField(max_length=254)
	def __str__ (self):
		return f"Ordonnance du Patient {self.id_patient.username}"

class certificat (models.Model):
	id_ordonnance = models.AutoField(primary_key=True)
	id_patient = models.ForeignKey(User, related_name="certificat", on_delete=models.CASCADE, null=True)
	date = models.DateTimeField()
	medicament = models.CharField(max_length=254)
	def __str__ (self):
		return f"Ordonnance du Patient {self.id_patient.username}"