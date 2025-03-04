from django.urls import path
from . import views

app_name = 'checkins'

urlpatterns = [
    # Listagem e detalhes
    path('', views.CheckinListView.as_view(), name='checkin-list'),
    path('<int:pk>/', views.CheckinDetailView.as_view(), name='checkin-detail'),
    
    # Criação e upload de arquivos adicionais
    path('criar/', views.CheckinCreateView.as_view(), name='checkin-create'),
    path('<int:pk>/upload-arquivo/', views.CheckinArquivoUploadView.as_view(), name='checkin-upload-arquivo'),
    
    # Aprovação e rejeição
    path('<int:pk>/aprovar/', views.CheckinAprovarView.as_view(), name='checkin-aprovar'),
    path('<int:pk>/rejeitar/', views.CheckinRejeitarView.as_view(), name='checkin-rejeitar'),
    
    # Listagem de pendentes (para logística)
    path('pendentes/', views.CheckinPendentesView.as_view(), name='checkin-pendentes'),
]