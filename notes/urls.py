from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('notes/new/', views.add_note, name='add_note'),
    path('notes/<int:pk>/', views.note_detail, name='note_detail'),
    path('notes/<int:pk>/edit/', views.edit_note, name='edit_note'),
    path('notes/<int:pk>/delete/', views.delete_note, name='delete_note'),
    path('notes/<int:pk>/pdf/', views.export_pdf, name='export_pdf'),
    path('about/', views.about, name='about'),
]
