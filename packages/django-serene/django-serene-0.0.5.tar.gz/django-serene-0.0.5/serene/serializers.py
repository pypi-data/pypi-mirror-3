import datetime

from django.db import models
from djangorestframework.serializer import Serializer, _SkipField


# Inject/Override methods in djangorestframework Serializer.
# Necessary because OnTheFlySerializer is based on djangorestframework Serializer.
def links(self, instance):
    try:
        return {
            'self': {
                'href': instance.get_absolute_url(),
                'rel': 'self',
                'title': unicode(instance),
            }
        }
    except (AttributeError, NotImplementedError):
        raise _SkipField
Serializer.links = links

def title(self, instance):
    if isinstance(instance, models.Model):
        return unicode(instance)
    else:
        return instance['title']
Serializer.title = title

Serializer._serialize = Serializer.serialize
def serialize(self, obj):
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time,)):
        return obj.isoformat()
    else:
        return self._serialize(obj)
Serializer.serialize = serialize
# End djangorestframework method injection/override


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
                        'title': unicode(instance),
                    }
                },
            }
        else:
            return super(RelatedSerializer, self).serialize_model(instance)