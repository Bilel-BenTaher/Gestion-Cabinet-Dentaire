from django.shortcuts import render
from .forms import SignUpForm,PostForm,RdvForm,LoginForm
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from .models import Rdv
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import Group
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from datetime import date
from django.db.models import Max
# Create your views here.


def home(request):
	return render(request,'home.html')

from .models import FichePatient

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST or None)
        if form.is_valid():
            # Sauvegarde l'utilisateur
            user = form.save()

            # Création de la fiche de patient liée à l'utilisateur
            FichePatient.objects.create(
                id_patient=user,
                nom=user.last_name,
                prenom=user.first_name,
                age=form.cleaned_data['age'],
                sexe=form.cleaned_data['gender'],
                tel=form.cleaned_data['phone'],
                motif_consultation='',  # Vous pouvez définir un motif par défaut si nécessaire
            )

            # Authentifie l'utilisateur après l'inscription
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            # Redirection après l'inscription
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})

def login_view(request):
    form = LoginForm(request.POST or None)  # Instanciation du formulaire
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)  # Authentification
            
            if user is not None:
                login(request, user)  # Connexion de l'utilisateur
                
                # Redirection en fonction du rôle de l'utilisateur
                if user.is_staff:  # Si l'utilisateur est un membre du staff
                    return redirect('/admin/')  # Redirige vers l'administration Django
                else:
                    return redirect('/panel/')  # Redirige vers la page d'accueil ou une autre page
                
            else:
                # Ajouter un message d'erreur si l'authentification échoue
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    # Rendu du formulaire de connexion
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

from datetime import datetime

def CountNumeroRdvForDay(rdv_date):
    """
    Calcule le numéro du prochain rendez-vous pour une date spécifique.
    """
    rdvs_on_date = Rdv.objects.filter(date=rdv_date).order_by('num_rdv')
    last_rdv = rdvs_on_date.aggregate(Max('num_rdv'))['num_rdv__max']

    # Retourner le prochain numéro de rendez-vous (ou 1 si aucun rdv n'existe)
    return (last_rdv or 0) + 1


def rdv_new(request):
    form = PostForm(request.POST or None)

    if form.is_valid():
        rdv = form.save(commit=False)
        rdv.id_patient = request.user  # Associer l'utilisateur connecté
        rdv.date = form.cleaned_data['date']

        # Calculer le numéro et sauvegarder
        rdv.num_rdv = CountNumeroRdvForDay(rdv.date)
        rdv.save()  # `save` va automatiquement calculer l'heure via `calculate_time`
        return redirect('rdv_list')

    return render(request, 'panel.html', {'form': form})


@login_required
def rdv_list(request):
    # Récupérer les rendez-vous de l'utilisateur connecté ou de l'administrateur
    if request.user.is_superuser:
        rdv = Rdv.objects.all()  # Si l'utilisateur est admin, on récupère tous les rdv
    else:
        rdv = Rdv.objects.filter(id_patient=request.user.id)  # Sinon, on récupère les rdv de l'utilisateur connecté
    
    data = {}
    
    if not rdv:  # Si aucun rendez-vous n'existe
        data['no_rdv_message'] = "Vous n'avez pas de rendez-vous. Vous pouvez en prendre un maintenant."
        data['show_button'] = True  # Afficher le bouton pour prendre un rendez-vous
    else:
        data['object_list'] = rdv  # Sinon, afficher les rendez-vous existants

    return render(request, 'rdv_list.html', data)

@login_required
def rdv_create(request, template_name='rdv_form.html'):
    form = RdvForm(request.POST or None)


    if form.is_valid():
        rdv = form.save(commit=False)
        rdv.id_patient=request.user
        rdv.num_rdv=CountNumeroRdvForDay()
        rdv.save()
        return redirect('rdv_list')
    return render(request, template_name, {'form':form})

@login_required
def rdv_update(request, pk, template_name='rdv_form.html'):
    if request.user.is_superuser:
        rdv= get_object_or_404(Rdv, id=pk)
    else:
        rdv= get_object_or_404(Rdv, id=pk, id_patient=request.user)
    form = RdvForm(request.POST or None, instance=rdv)
    if form.is_valid():
        form.save()
        return redirect('rdv_list')
    return render(request, template_name, {'form':form})

@login_required
def rdv_delete(request, pk, template_name='rdv_confirm_delete.html'):
    if request.user.is_superuser:
        rdv= get_object_or_404(Rdv, id=pk)
    else:
        rdv= get_object_or_404(Rdv, id=pk, id_patient=request.user)
        print (rdv)
    if request.method=='POST':
        rdv.delete()
        return redirect('rdv_list')
    return render(request, template_name, {'object':rdv})

import textwrap
from django.conf import settings  # Importer settings de Django
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import arabic_reshaper
from bidi.algorithm import get_display
from django.http import HttpResponse
from .models import Ordonnance  # Assurez-vous d'importer correctement votre modèle Ordonnance

def generate_ordonnance_pdf(request, ordonnance_id):
    # Récupérer l'ordonnance et les données associées
    ordonnance = Ordonnance.objects.get(id_ordonnance=ordonnance_id)
    patient = ordonnance.id_patient
    medicament = ordonnance.medicament
    cabinet_adresse = "Adresse du Cabinet"
    doctor_name_fr = "Docteur Foulen BEN FALTEN\nMédecin Dentiste"
    doctor_name_ar = "دكتور فلان بن فلتان\nطبيب أسنان"

    # Récupérer le chemin absolu vers la police dans le dossier static
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Amiri-Regular.ttf')
    
    # Enregistrer la police arabe dans ReportLab
    try:
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Amiri', font_path))  # Enregistrer la police
        else:
            raise FileNotFoundError(f"Font file not found at {font_path}")
    except Exception as e:
        print(f"Error loading font: {e}")
        return HttpResponse("Font file loading error", status=500)

    # Créer une réponse pour envoyer le PDF en tant que page imprimable
    response = HttpResponse(content_type='application/pdf')
    # Supprimer l'en-tête Content-Disposition pour éviter le téléchargement automatique
    # Cela permet au navigateur d'ouvrir le PDF dans un visualiseur intégré ou d'imprimer directement
    # response['Content-Disposition'] = f'attachment; filename="ordonnance_{ordonnance.id_ordonnance}.pdf"'

    # Créer un objet canvas pour générer le PDF
    c = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Définir la police pour le texte en français (gras pour "Docteur" et "Médecin Dentiste")
    c.setFont("Helvetica-Bold", 14)

    # Haut de la page - Nom du médecin en français centré à gauche
    c.drawString(60, height - 20, "Docteur")  # "Docteur" en gras
    c.setFont("Helvetica-Bold", 14)  # Garder "Foulen BEN FALTEN" en gras
    c.drawString(30, height - 40, "Foulen BEN FALTEN")  # "Foulen BEN FALTEN" en gras
    c.setFont("Helvetica", 12)  # Revenir à la police normale
    c.drawString(50, height - 60, "Médecin Dentiste")  # "Médecin Dentiste" en texte normal

    # Définir la police pour le texte en arabe (Amiri)
    c.setFont("Amiri", 12)
    
    # Reshaper et Bidi pour gérer correctement l'arabe
    reshaped_text = arabic_reshaper.reshape("دكتور")  # Reshape le texte arabe
    bidi_text = get_display(reshaped_text)  # Applique le processus bidi pour afficher de droite à gauche

    # Nom arabe centré à droite
    c.drawString(width-75, height - 20, bidi_text)  # Affiche le texte arabe "دكتور" de droite à gauche
    c.setFont("Amiri", 12)  # Revenir à la police normale pour la suite
    reshaped_text2 = arabic_reshaper.reshape("فلان بن فلتان")  # Reshape le texte arabe
    bidi_text2 = get_display(reshaped_text2)  # Applique le processus bidi pour afficher de droite à gauche
    c.drawString(width - 90, height - 40, bidi_text2)  # Affiche "فلان بن فلتان"
    c.setFont("Amiri", 12)  # Toujours utiliser la police normale
    reshaped_text3 = arabic_reshaper.reshape("طبيب أسنان")  # Reshape "طبيب أسنان"
    bidi_text3 = get_display(reshaped_text3)  # Applique le processus bidi pour afficher de droite à gauche
    c.drawString(width - 90, height - 60, bidi_text3)  # Affiche "طبيب أسنان"

    # Ligne de séparation sous le nom du médecin
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(32, height - 80, width - 32, height - 80)

    # Contenu principal - Détails du patient et médicaments
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 100, "Ordonnance Médicale")  # Ajouter "Ordonnance Médicale" centré

    # Contenu principal - Détails du patient et médicaments
    c.setFont("Helvetica", 12)
    c.drawString(30, height - 120, f"Patient : {patient.first_name} {patient.last_name}")
    c.drawString(30, height - 140, f"Tunis le {ordonnance.date.strftime('%d/%m/%Y')}")
    
    # Séparer "Médicaments :" du texte des médicaments
    medicament_title = "Médicaments :"
    medicament_body = medicament  # Le reste des médicaments

    # Découper le texte des médicaments en lignes
    wrapped_medicament = textwrap.wrap(medicament_body, width=80)  # Ajustez `width` selon la largeur souhaitée

    # Position initiale pour afficher les lignes
    current_y = height - 160
    line_spacing = 15  # Espacement entre les lignes

    # Affichage du titre "Médicaments :" à la première position
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, current_y, medicament_title)
    current_y -= line_spacing  # Espacer pour la ligne suivante

    # Affichage des lignes de médicaments
    c.setFont("Helvetica", 12)
    for line in wrapped_medicament:
        c.drawString(30, current_y, line)
        current_y -= line_spacing  # Déplacer la position vers le bas pour la ligne suivante

    # Exemple d'adresses
    cabinet_adresse_fr = "123 Rue Exemple, Ville, Code Postal, Pays"  # Adresse en français
    cabinet_adresse_ar = "شارع المثال 123، المدينة، الرمز البريدي، البلد"  # Adresse en arabe

    # Bas de page - Adresse en français
    c.setFont("Helvetica", 12)
    c.drawString(30, 25, f"Adresse: {cabinet_adresse_fr}")

    # Bas de page - Adresse en arabe (alignée à droite)
    c.setFont("Amiri", 12)
    reshaped_address_ar = arabic_reshaper.reshape(f"عنوان:{cabinet_adresse_ar}")  # Reshape l'adresse en arabe
    bidi_address_ar = get_display(reshaped_address_ar)  # Applique le processus bidi pour afficher de droite à gauche
    c.drawRightString(width - 30, 25, bidi_address_ar)  # Affiche l'adresse arabe alignée à droite

    # Ajouter l'email à gauche
    email = "exemple@email.com"  # Remplacez par l'email réel
    c.setFont("Helvetica", 10)
    c.drawString(30, 10, f"Email : {email}")

    # Ajouter le numéro GSM à droite
    gsm = "+212 6 12 34 56 78"  # Remplacez par le numéro GSM réel
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 30, 10, f"GSM : {gsm}")

    # Ligne de séparation finale ajustée
    c.setStrokeColor(colors.black)
    c.line(30, 40, width - 30, 40)  # Ligne juste au-dessus de l'email et du GSM (ajustée plus près)

    # Sauvegarder le PDF
    c.showPage()
    c.save()

    return response






