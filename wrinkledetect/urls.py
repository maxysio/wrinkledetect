from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.CreateImageAnalysisView.as_view(), name='index'),
    path('analysis/<int:pk>', views.ShowImageAnalysisView.as_view(), name='analysis')
]

