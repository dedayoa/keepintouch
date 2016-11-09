from django.db import models

# Create your models here.



class CallStatus(models.Model):
    
    job_uuid = models.UUIDField(primary_key=True)
    status = models.TextField(blank=True)
    
    caller = models.ForeignKey('core.KITUser', on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    
    
class CallHistory(models.Model):
    # formerly FailedCall Model
    
    status = models.CharField(max_length=20)
    description = models.CharField(max_length=255, blank=True)
    
    caller = models.ForeignKey('core.KITUser', on_delete=models.SET_NULL, null=True)
    last_modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)