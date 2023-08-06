from django.db import models
from djangorestframework.resources import ModelResource as DrfModelResource
from serene.serializers import RelatedSerializer


class ModelResource(DrfModelResource):
    exclude = ()
    include = ('links',)
    related_serializer = RelatedSerializer

    def links(self, instance):
        links = {}
        # Add self link
        try:
            links['self'] = {
                'href': self.url(instance),
                'rel': 'self',
                'title': unicode(instance),
            }
        except (AttributeError, NotImplementedError):
            pass
        # Add related instances' links
        for field in instance._meta.fields:
            if isinstance(field, models.ForeignKey):
                name = field.name
                obj = getattr(instance, name)
                try:
                    links[name] = {
                        'href': obj.get_absolute_url(),
                        'rel': name,
                        'title': unicode(obj),
                    }
                except (AttributeError, NotImplementedError):
                    pass
        return links

    def url(self, instance):
        return instance.get_absolute_url()
