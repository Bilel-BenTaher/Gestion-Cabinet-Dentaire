from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from pages.models import Rdv
from django.forms.widgets import SelectDateWidget
from django.contrib.admin import widgets                                       
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm
from django.forms.widgets import DateInput

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        required=False, 
        label='', 
        widget=forms.TextInput(attrs={
            'placeholder': 'Prénom',
            'style': 'width: 215px; color: black;',
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False, 
        label='', 
        widget=forms.TextInput(attrs={
            'placeholder': 'Nom',
            'style': 'width: 215px; color: black;',
        })
    )
    username = forms.CharField(
        max_length=150,
        label='', 
        widget=forms.TextInput(attrs={
            'placeholder': "Nom d'utilisateur",
            'style': 'width: 215px; color: black;',
        })
    )
    age = forms.IntegerField(
        required=True, 
        label='', 
        widget=forms.NumberInput(attrs={
            'placeholder': 'Âge',
            'style': 'width: 215px; color: black;',
        })
    )
    gender = forms.ChoiceField(
    required=True, 
    label='', 
    choices=[('', 'Sélectionnez votre genre'), ('M', 'Homme'), ('F', 'Femme')],
    widget=forms.Select(attrs={
        'style': 'width: 215px; color: gray;',  # Placeholder par défaut en gris
        'class': 'gender-select',  # Classe pour plus de contrôle
        'onchange': "this.style.color = this.value === '' ? 'gray' : 'black';",  # Couleur noire si une option est sélectionnée
    })
)

    phone = forms.CharField(
        max_length=15, 
        required=True, 
        label='', 
        widget=forms.TextInput(attrs={
            'placeholder': 'Numéro de téléphone',
            'style': 'width: 215px; color: black;',
        })
    )
    password1 = forms.CharField(
        label='', 
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mot de passe',
            'style': 'width: 215px; color: black;',
        })
    )
    password2 = forms.CharField(
        label='', 
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirmer le mot de passe',
            'style': 'width: 215px; color: black;',
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'age', 'gender', 'phone', 'password1', 'password2')



class PostForm(forms.ModelForm):
    class Meta:
        model = Rdv
        fields = ['date']

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # Applique un widget DateInput avec un format spécifique et ajoute la classe CSS 'datepicker'
        self.fields['date'].widget = DateInput(attrs={
            'class': 'datepicker',  # Classe CSS pour le calendrier
            'type': 'date',  # Utilise le type HTML5 'date' pour le champ
            'placeholder': 'Choisir une date',  # Texte d'aide pour l'utilisateur
        })

class RdvForm(forms.ModelForm):
    
    class Meta:
        model = Rdv
        fields = ['date', 'num_rdv']

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label='',  # Ne pas afficher de label
        widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur",'style': 'width: 215px; color: black;',})
    )
    password = forms.CharField(
        label='',  # Ne pas afficher de label
        widget=forms.PasswordInput(attrs={'placeholder': "Mot de passe",'style': 'width: 215px; color: black;',})
    )


# class RdvCreateForm(forms.ModelForm):
# 		class Meta:
# 				model = Rdv
# 			   exclude = ('id_secretaire',)
# 		def __init__(self, *args, **kwargs):
# 				self.request = kwargs.pop('request', None)
# 				super(RdvCreateForm, self).__init__(*args, **kwargs)

# class RdvUpdateForm(forms.ModelForm):
# 		class Meta:
# 				model = Rdv
		

# 		def __init__(self, *args, **kwargs):
# 				self.request = kwargs.pop('request', None)
# 				super(RdvUpdateForm, self).__init__(*args, **kwargs)




