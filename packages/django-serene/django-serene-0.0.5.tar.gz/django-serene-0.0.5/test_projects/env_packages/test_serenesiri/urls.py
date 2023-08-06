from django.conf.urls.defaults import patterns, include, url
from serene.views import CreatableInstanceModelView, PaginatedListOrCreateModelView

from test_serenesiri.resources import BrandResource, ProductResource

urlpatterns = patterns('',
    url(r'^brands/?$', PaginatedListOrCreateModelView.as_view(resource=BrandResource), name='brand_list_or_create'),
    url(r'^brands/(?P<id>\d+)/?$', CreatableInstanceModelView.as_view(resource=BrandResource), name='brand_instance'),
    url(r'^products/?$', PaginatedListOrCreateModelView.as_view(resource=ProductResource), name='product_list_or_create'),
    url(r'^products/(?P<id>\d+)/?$', CreatableInstanceModelView.as_view(resource=ProductResource), name='product_instance'),
)
