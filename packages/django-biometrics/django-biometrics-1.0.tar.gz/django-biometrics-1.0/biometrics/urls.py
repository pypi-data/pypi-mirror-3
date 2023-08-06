from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',
    url(r'^user/(?P<user>\d+)/fingerprints/$', views.handle, 
        name="biometrics_handle_fingerprints"),
)