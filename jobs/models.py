from django.db import models


class job(models.Model):
    hash = models.CharField(max_length=100)
    resultid = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True) # When it was create
    updated_at = models.DateTimeField(auto_now=True)     # When i was update
    creator  = models.ForeignKey('auth.User', related_name='jobs', on_delete=models.CASCADE)
    # resultid = models.ForeignKey('django_celery_results.TaskResult', related_name='jobid', on_delete=models.CASCADE,default='0')





