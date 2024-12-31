from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FichePatient, Consultation
from django.utils.timezone import now

@receiver(post_save, sender=FichePatient)
def create_consultation(sender, instance, created, **kwargs):
    if instance.valide and created:
        print("FichePatient validée, création d'une consultation.")  # Debug
        # Crée une consultation pour chaque patient dont la fiche a été validée
        Consultation.objects.create(
            id_patient=instance.id_patient,
            id_facture=None,  # Vous pouvez ajouter une logique pour associer une facture si nécessaire
            contenue="Consultation générée automatiquement",
            traitement="Aucun traitement spécifié",
            date_consultation=now().date()  # Utilise la date actuelle
        )
