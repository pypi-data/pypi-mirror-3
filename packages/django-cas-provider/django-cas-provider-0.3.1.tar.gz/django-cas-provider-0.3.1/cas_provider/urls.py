from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('cas_provider.views',
    url(r'^login/?$', 'login', name='cas_login'),
    url(r'^validate/?$', 'validate', name='cas_validate'),
    url(r'^proxy/?$', 'proxy', name='proxy'),
    url(r'^serviceValidate/?$', 'service_validate', name='cas_service_validate'),
    url(r'^proxyValidate/?$', 'proxy_validate', name='cas_proxy_validate'),
    url(r'^logout/?$', 'logout', name='cas_logout'),
)
