from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^complete/$', 'cccontact.views.complete', name='complete'),
    url(r'^$', 'cccontact.views.contact', name='contact')
)
