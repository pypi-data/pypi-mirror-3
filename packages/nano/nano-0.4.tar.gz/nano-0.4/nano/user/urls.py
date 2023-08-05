from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

signup_done_data = { 'template': 'nano/user/signup_done.html' }

# 'project_name' should be a setting
password_reset_data = {'project_name': 'CALS'}

urlpatterns = patterns('nano.user.views',
    (r'^signup/$',          'signup', {}, 'nano_user_signup'),
    (r'^signup/done/$',     direct_to_template, signup_done_data, 'nano_user_signup_done'),
    (r'^password/reset/$',  'password_reset', password_reset_data, 'nano_user_password_reset'),
    (r'^password/change/$', 'password_change', {}, 'nano_user_password_change'),
)
