from serene import models

class DummyModel(models.Model):
    name = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.name

