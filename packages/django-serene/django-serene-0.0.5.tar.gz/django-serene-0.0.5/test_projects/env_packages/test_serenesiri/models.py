from serene import models


class Brand(models.Model):
    name = models.CharField(max_length=1024)
    code = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('brand_instance', (), {'id': self.id})

class Product(models.Model):
    name = models.CharField(max_length=1024)
    code = models.CharField(max_length=1024)
    color = models.CharField(max_length=1024)
    brand = models.ForeignKey(Brand)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('product_instance', (), {'id': self.id})