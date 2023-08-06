from django.db import models

import picklefield

class FTManager(models.Manager):
    def create_with_serialized_data(self, data, **kwargs):
        data = data.decode('base64')
        return self.create(data=data, **kwargs)
    
class FingerprintTemplate(models.Model):
    user = models.OneToOneField('auth.User', 
        related_name='fingerprint_template')
    data = picklefield.fields.PickledObjectField()
    
    objects = FTManager()
    class Meta:
        app_label = 'biometrics'
        db_table = 'biometrics_fingerprint_templates'
        
    def __unicode__(self):
        return "Fingerprint template of %s" % self.user.name
    
    
    def _get_serialized_data(self):
        return self.data.encode('base64')
    def _set_serialized_data(self, data):
        self.data = data.decode('base64')
    
    serialized_data = property(_get_serialized_data, _set_serialized_data)