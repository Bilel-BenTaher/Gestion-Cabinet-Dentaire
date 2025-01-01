from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
     path('', views.home, name='home'),
     path('signup/', views.signup, name='signup'),
     path('login/', views.login_view, name='login'),
     path('logout/', views.logout_view, name='logout'),
     path('panel/', views.rdv_list, name='rdv_list'),
     path('rdv/new/', views.rdv_new, name='rdv_new'),
     path('rdv/edit/<int:pk>/', views.rdv_update, name='rdv_edit'),
    path('rdv/delete/<int:pk>/', views.rdv_delete, name='rdv_delete'),
     path('ordonnance/pdf/<int:ordonnance_id>/', views.generate_ordonnance_pdf, name='generate_ordonnance_pdf'),
     ]
