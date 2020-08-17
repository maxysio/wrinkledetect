from django.db import models
import os
from .validators import validate_file_extension

# Create your models here.


class ImageDetails(models.Model):
    img_fn = models.ImageField(verbose_name='Select Image', upload_to='upload_img',
                               null=True, validators=[validate_file_extension])

    def __str__(self):
        return os.path.splitext(self.img_fn.name)[1]


class ImageAnalysis(models.Model):
    
    image = models.ForeignKey(
        ImageDetails, verbose_name='Input Image: ', on_delete=models.CASCADE)
    
    img_seat_serial = models.CharField(
        verbose_name='Seat Serial Id', null=True, max_length=50)
    img_analysis_json = models.TextField(
        verbose_name='Analysis JSON')
    img_anly_fn = models.ImageField(
        verbose_name='Analyzed Image', upload_to='upload_img', null=True, validators=[validate_file_extension])
    img_anly_start_time = models.TimeField(
        verbose_name='Start Time: ', auto_now=True)
    img_anly_end_time = models.TimeField(
        verbose_name='End Time: ', auto_now=True)
    img_anly_exec_time = models.DecimalField(
        verbose_name='Execution Duration: ', default=0, decimal_places=10, max_digits=30)
    num_objects = models.IntegerField(verbose_name='Number of Wrinkles: ', default=0)

    def __str__(self):
        return os.path.splitext(self.image.img_fn.name)[1]
