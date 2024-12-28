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

# Create your views here.


def home(request):
	return render(request,'home.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST or None)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
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
                    return redirect('home')  # Redirige vers la page d'accueil ou une autre page
                
            else:
                # Ajouter un message d'erreur si l'authentification échoue
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    # Rendu du formulaire de connexion
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def rdv_new(request):
    form = PostForm(request.POST or None)  # Si la requête est POST, charge les données

    if form.is_valid():
        rdv = form.save(commit=False)
        rdv.id_patient = request.user  # Associer l'utilisateur connecté
        rdv.id_secretaire = request.user  # Assigner l'utilisateur connecté comme secrétaire
        rdv.num_rdv = CountNumeroRdv()  # Utilise la fonction CountNumeroRdv pour définir le numéro
        rdv.save()  # Sauvegarder le rendez-vous

        return redirect('rdv_list')  # Rediriger vers la liste des rendez-vous après la sauvegarde

    context = {
        'form': form,  # Le formulaire est passé au template pour être affiché
    }

    return render(request, 'panel.html', context)  # Rendu du template si le formulaire n'est pas valide


 
def CountNumeroRdv():
        no = Rdv.objects.count()
        if no == None:
            return 1
        else:
            return no + 1

@login_required
def rdv_list(request, template_name='rdv_list.html'):
    if request.user.is_superuser:
        rdv = Rdv.objects.all()
    else:
        rdv = Rdv.objects.filter(id_patient=request.user.id)
    data = {}
    data['object_list'] = rdv
    return render(request, template_name, data)

@login_required
def rdv_create(request, template_name='rdv_form.html'):
    form = RdvForm(request.POST or None)


    if form.is_valid():
        rdv = form.save(commit=False)
        rdv.id_patient=request.user
        rdv.num_rdv=CountNumeroRdv()
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