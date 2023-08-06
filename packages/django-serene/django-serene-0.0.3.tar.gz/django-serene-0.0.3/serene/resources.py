from django.db import models
from djangorestframework.resources import ModelResource as DrfModelResource
from serene.serializers import RelatedSerializer


class ModelResource(DrfModelResource):
    exclude = ()
    include = ('links',)
    related_serializer = RelatedSerializer

    def filter_response(self, obj):
        self._links = {}
        return super(ModelResource, self).filter_response(obj)

    def links(self, instance):
        self._links['self'] = {
            'href': self.url(instance),
            'rel': 'self',
            }
        return self._links

    def url(self, instance):
        return instance.get_absolute_url()

    def serialize_val(self, key, obj):
        serialized_val = super(ModelResource, self).serialize_val(key, obj)
        if isinstance(obj, models.Model):
            self._links[key] = {
                'href': serialized_val['links']['self']['href'],
                'rel': key,
                'title': serialized_val['title'],
            }
            return serialized_val
        else:
            return serialized_val