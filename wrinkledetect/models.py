from django.db import models
import os
from .validators import validate_file_extension

# Create your models here.

class ImageAnalysis(models.Model):
    img_fn = models.FileField('Upload Resume', upload_to='upload_img', null=True, validators=[validate_file_extension])
    img_analysis_json = models.TextField(verbose_name='Analysis JSON', null=True)

    def __str__(self):
        return os.path.splitext(self.img_fn.name)[1]