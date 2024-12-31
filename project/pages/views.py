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