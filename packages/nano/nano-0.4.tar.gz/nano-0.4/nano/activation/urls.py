from django.conf.urls.defaults import *

urlpatterns = patterns('nano.activation.views',
    url(r'^activate$',         'activate_key', name='nano-activate-key'),
)

urlpatterns += patterns('',
    url(r'^activation_ok/$', 'django.views.generic.simple.direct_to_template', 
            {'template': 'nano/activation/activated.html'
            }, name='nano-activation-ok'),
)

