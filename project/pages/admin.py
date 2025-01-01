# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from pages.models import FichePatient, CabinetDentaire, Rdv, Consultation, Facture, Ordonnance,certificat
from django import forms
from django.forms import ModelForm, PasswordInput
from django.contrib.auth.models import User

from django.contrib import admin
from pages.models import FichePatient, CabinetDentaire, Rdv, Consultation, Facture, Ordonnance
from django import forms
from django.contrib.admin import SimpleListFilter


# Filtre personnalisé pour afficher les rendez-vous par date
class DateRdvFilter(SimpleListFilter):
    title = 'Date de rendez-vous'
    parameter_name = 'date'

    def lookups(self, request, model_admin):
        return [
            ('aujourdhui', 'Aujourd\'hui'),
            ('demain', 'Demain'),
        ]

    def queryset(self, request, queryset):
        from datetime import date, timedelta

        if self.value() == 'aujourdhui':
            return queryset.filter(date=date.today())
        elif self.value() == 'demain':
            return queryset.filter(date=date.today() + timedelta(days=1))
        return queryset


class RdvAdmin(admin.ModelAdmin):
    list_display = ('id_patient', 'date', 'time', 'num_rdv')
    search_fields = ['id_patient__username']
    ordering = ['date', 'num_rdv']  # Ordre de tri par défaut
    list_filter = ('date', DateRdvFilter)  # Ajout du filtre personnalisé pour la date
    exclude = ('id_patient',)
    def get_queryset(self, request):
        """
        Permet d'afficher les rendez-vous en fonction de la date choisie, tout en maintenant un tri par date et num_rdv.
        """
        qs = super().get_queryset(request)
        # Applique le tri par défaut si aucun filtre spécifique n'est appliqué
        if not request.GET.get('date'):  # Si aucun filtre 'date' n'est appliqué
            qs = qs.order_by('date', 'num_rdv')  # Assure que le tri par défaut est appliqué
        return qs
    
class FactureConsultation(admin.ModelAdmin):
    # Définir les champs à afficher dans la vue liste
    list_display = ('id_patient', 'prix')

    # Définir les champs de recherche
    search_fields = ['id_patient__username', 'consultation__fiche_patient__nom']

    

    

# Personnalisation de l'administration pour Consultation
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ( 'id_patient',  'date_consultation', 'valide')
    list_filter = ('valide', 'date_consultation')  # Ajout d'un filtre pour voir les consultations validées ou non
    search_fields = ['id_patient__username', 'contenue']  # Permet de rechercher par patient ou contenu de la consultation
    exclude = ('id_patient',)
    def get_queryset(self, request):
        """
        Modifie la liste des objets affichés pour n'inclure que les consultations non validées par défaut.
        """
        qs = super().get_queryset(request)
        return qs.filter(valide=False)  # Affiche seulement les consultations non validées

    actions = ['valider_consultations', 'invalider_consultations']

    @admin.action(description='Valider les consultations sélectionnées')
    def valider_consultations(self, request, queryset):
        queryset.update(valide=True)

    @admin.action(description='Invalider les consultations sélectionnées')
    def invalider_consultations(self, request, queryset):
        queryset.update(valide=False)

from django.contrib import admin
from django.utils.html import format_html
from .models import Ordonnance

class OrdonnanceAdmin(admin.ModelAdmin):
    list_display = ('patient_full_name', 'date', 'print_button')
    search_fields = ['id_patient__first_name', 'id_patient__last_name']

    def patient_full_name(self, obj):
        return f"{obj.id_patient.first_name} {obj.id_patient.last_name}"
    patient_full_name.short_description = "Nom et Prénom"

    def print_button(self, obj):
        return format_html(
            '<a class="button" href="/ordonnance/pdf/{}/" target="_blank">Imprimer </a>',
            obj.id_ordonnance
        )
    print_button.short_description = "Imprimer"
    print_button.allow_tags = True

# Enregistrement des modèles dans l'administration
admin.site.register(CabinetDentaire)
admin.site.register(FichePatient)
admin.site.register(Rdv, RdvAdmin)
admin.site.register(Consultation, ConsultationAdmin)
admin.site.register(Facture, FactureConsultation)
admin.site.register(Ordonnance, OrdonnanceAdmin)
admin.site.register(certificat)

