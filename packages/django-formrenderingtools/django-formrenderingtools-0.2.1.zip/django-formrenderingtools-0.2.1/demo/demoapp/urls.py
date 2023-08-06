from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'django.views.generic.simple.direct_to_template',
        {'template': 'demoapp/index.html'}, name='simple_builtin'),
)

urlpatterns += patterns('demo.demoapp.views',
    url(r'^simple/$', 'simple', name='simple'),
    url(r'^errors/$', 'errors', name='errors'),
    url(r'^as-table/$', 'as_table', name='as_table'),
    url(r'^as-ul/$', 'as_ul', name='as_ul'),
    url(r'^as-p/$', 'as_p', name='as_p'),
    url(r'^fields-order/$', 'fields_order', name='fields_order'),
    url(r'^fieldsets/$', 'fieldsets', name='fieldsets'),
    url(r'^two-custom-fields/$', 'two_custom_fields', name='two_custom_fields'),
    url(r'^altering all elements/$', 'altering_all_elements', name='altering_all_elements'),
)
