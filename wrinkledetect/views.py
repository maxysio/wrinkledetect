from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect

from .models import ImageAnalysis

# Create your views here.

class CreateImageAnalysisView(generic.CreateView):
    fields = ['img_fn']
    model = ImageAnalysis
    template_name = "wrinkledetect/index.html"
    
    def get_success_url(self):
        return reverse('index')
