from .models import ImageAnalysis, ImageDetails
import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
import time

import json
from ibm_watson import VisualRecognitionV4, ApiException
from ibm_watson.visual_recognition_v4 import AnalyzeEnums, FileWithMetadata
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from pyzbar.pyzbar import decode
import cv2
from zipfile import ZipFile
from PIL import Image, ImageDraw
import matplotlib
matplotlib.use('Agg')


# Create your views here.

class CreateImageAnalysisView(generic.CreateView):
    fields = ['img_fn']
    model = ImageDetails
    template_name = 'wrinkledetect/index.html'

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.save()

        img_analysis = ImageDetails.objects.filter(
            img_fn=str(self.object.img_fn))[0]

        return HttpResponseRedirect(reverse('analysis', args=[str(img_analysis.id)]))


class ShowImageAnalysisView(generic.DetailView):
    model = ImageDetails
    template_name = 'wrinkledetect/analysis.html'

    def get_context_data(self, **kwargs):
        context = super(ShowImageAnalysisView, self).get_context_data(**kwargs)

        # Get the image object
        img = get_object_or_404(ImageDetails, pk=str(self.kwargs['pk']))
        img_anly_fn = img.img_fn.name
        len_wrinkles = 0

        # Analyze the Image
        resp = AnalyzeImage(img)

        # Check for errors
        if('Error' in resp):
            context['Error'] = resp['Error']
        else:
            # Check if there are any wrinkles
            if(resp['num_objects']) > 0:
                # Get all the wrinkles detected in the image
                wrinkles = resp['images'][0]['objects']['collections'][0]['objects']
            else:
                wrinkles = []

            # Create a new analyzed image with the wrinkles
            # detected on it
            img_anly_fn = CreateAnalyzedFile(img, wrinkles)

            # Create an anlyzed image with all the wrinkles on it
            img = ImageAnalysis.objects.create(image=img, img_seat_serial=resp['seat_serail'],
                                               img_analysis_json=resp, img_anly_fn=img_anly_fn,
                                               img_anly_start_time=resp['start_time'],
                                               img_anly_end_time=resp['end_time'],
                                               img_anly_exec_time=resp['exec_time'],
                                               num_objects=resp['num_objects'])

        context['img_anly'] = img

        return context


def CreateAnalyzedFile(img, wrinkles):

    just_fn = img.img_fn.name.split('.')[0]
    fn_ext = img.img_fn.name.split('.')[1]
    img_anly_fn = just_fn + '_anly.' + fn_ext

    im = np.array(Image.open(settings.MEDIA_ROOT + '/' +
                             img.img_fn.name), dtype=np.uint8)
    fig, ax = plt.subplots(1)
    ax.imshow(im)

    for w in wrinkles:
        left, top, width, height = w['location']['left'], w['location'][
            'top'], w['location']['width'], w['location']['height']
        rect = patches.Rectangle(
            (left, top), width, height, linewidth=2, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
        plt.text(left, top-15, str(round(float(w['score'])*100,2))+'%', color='red', fontsize=55)

    plt.axis('off')
    plt.gcf().set_size_inches(56, 42)
    plt.savefig(settings.MEDIA_ROOT + '/' + img_anly_fn, bbox_inches='tight')

    return img_anly_fn


def AnalyzeImage(img_fn):

    # Authenticate with IBM Watson
    
    #authenticator = IAMAuthenticator(
    #    'PROVIDE YOUR API KEY')
    
    visual_recognition = VisualRecognitionV4(
        version='2019-02-11', authenticator=authenticator)

    #visual_recognition.set_service_url(
    #    'PROVIDE YOUR SERVICE URL')


    zipFile = ZipFile(settings.MEDIA_ROOT + '/' +
                      img_fn.img_fn.name + '.zip', 'w')
    zipFile.write(settings.MEDIA_ROOT + '/' + img_fn.img_fn.name)
    zipFile = None

    img_file = open(settings.MEDIA_ROOT + '/' +
                    img_fn.img_fn.name + '.zip', 'rb')

    objs = {}
    execution_start_time = time.time()
    execution_time = 0

    try:
        resp = visual_recognition.analyze(collection_ids=["399edcc3-e1bb-46b7-9ce8-6e5acf56a43c"],
                                          features=[
                                              AnalyzeEnums.Features.OBJECTS.value],
                                          images_file=[FileWithMetadata(img_file)], threshold=0.25).get_result()

        execution_end_time = time.time()
        execution_time = round(execution_end_time - execution_start_time, 2)
        resp['start_time'] = str(time.asctime(
            time.localtime(execution_start_time)))
        resp['end_time'] = str(time.asctime(
            time.localtime(execution_end_time)))
        resp['exec_time'] = str(execution_time)

        if('collections' in resp['images'][0]['objects']):
            resp['num_objects'] = len(
                resp['images'][0]['objects']['collections'][0]['objects'])
        else:
            resp['num_objects'] = 0

        resp['seat_serail'] = GetBarCode(img_fn)

        return resp
    except ApiException as ex:
        objs['Error'] = "API failed with status code " + \
            str(ex.code) + ": " + ex.message
        return objs


def GetBarCode(img):
    image = cv2.imread(settings.MEDIA_ROOT + '/' + img.img_fn.name)
    detectedBarcodes = decode(image)

    # Return the first barcode you get
    for barcode in detectedBarcodes:
        (x, y, w, h) = barcode.rect
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 5)
        return str(barcode.data)[2:-1]

    return ''
