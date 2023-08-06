from serene.resources import ModelResource
from test_serenesiri.models import Brand, Product

class BrandResource(ModelResource):
    model = Brand

class ProductResource(ModelResource):
    model = Product