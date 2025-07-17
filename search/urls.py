from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('data_load/', views.data_load, name='data_load'),
    path('import_data/', views.import_data_view, name='import_data'),
    path('names/', views.search_names, name='search_names'),
    path('nrn/', views.search_nrn, name='search_nrn'),
]
