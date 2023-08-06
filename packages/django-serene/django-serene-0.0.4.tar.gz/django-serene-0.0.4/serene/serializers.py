import datetime

from django.db import models
from djangorestframework.serializer import Serializer as DrfSerializer


class Serializer(DrfSerializer):

    def serialize(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date, datetime.time,)):
            return obj.isoformat()
        else:
            return super(Serializer, self).serialize(obj)


class RelatedSerializer(Serializer):

    def serialize_model(self, instance):
        """
        serialize_model serializes both Model and dict.
        """
        if isinstance(instance, models.Model):
            return {
                'id': instance.id,
                'title': unicode(instance),
                'links': {
                    'self': {
                        'href': instance.get_absolute_url(),
                        'rel': 'self',
                    }
                },
            }
        else:
            return super(RelatedSerializer, self).serialize_model(instance)