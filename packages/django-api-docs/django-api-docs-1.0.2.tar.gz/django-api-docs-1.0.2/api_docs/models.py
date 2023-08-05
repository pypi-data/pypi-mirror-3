from django.db import models
from django.db.models.query import QuerySet
from api_docs.choices import *
from slugs import *

class APIMethodMixin(object):

    def published(self):
        return self.filter(published=True)
    
class APIMethodQuerySet(QuerySet, APIMethodMixin):
    pass

class APIMethodManager(models.Manager, APIMethodMixin):
    def get_query_set(self):
        return APIMethodQuerySet(self.model, using=self._db)


class APIDoc(models.Model):
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
    
class APIObject(models.Model):
    name = models.CharField(max_length=200)
    api_doc = models.ForeignKey(APIDoc)
    
    def __unicode__(self):
        return self.name
    

class Parameter(models.Model):
    name = models.CharField(max_length=120, help_text="The actual name of the paramter, always lower case")
    slug = models.SlugField(editable=False)
    type = models.CharField(max_length=20, choices=PARAM_TYPE)
    required = models.BooleanField()
    default_value = models.CharField(max_length=200, blank=True)
    var_type = models.CharField(max_length=20, choices=VAR_TYPE)
    get_or_url = models.CharField(max_length=20, choices=VAR_PLACEMENT)
    description = models.CharField(max_length=300)
    
    
    def __unicode__(self):
        return self.name
    
    def save(self):
        unique_slugify(self, self.name)
        super(Parameter, self).save()


class APIMethod(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(editable=False)
    type = models.CharField(max_length=10, choices=HTTP_METHOD)
    api_object = models.ForeignKey(APIObject)
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    display_url = models.CharField(max_length=300, help_text="This is the URL shown in docs, usually so you can add {item_id} where you would place a variable.")
    api_url = models.URLField(verify_exists=False, help_text="URL called for interactive docs, must be working API URL")
    parameter = models.ManyToManyField(Parameter, blank=True)
    published = models.BooleanField()
    
    objects = APIMethodManager()
    
    def __unicode__(self):
        return self.name
    
    def save(self):
        unique_slugify(self, self.name)
        super(APIMethod, self).save()
    
    
    
    
    
