from mongoengine import *

__all__ = ['DynamicFields', 'has_dfields']



def has_dfields(cls):
    cls._dfields = DynamicFields._dfields(cls.__name__)
    return cls

# Create your models here.
class DynamicFields(Document):
    refer = StringField(max_length=120, required=True) 
    name = StringField(max_length=120, required=True)
    typo = StringField(required=True)
    max_length = IntField()
    min_value = IntField()
    max_value = IntField()
    required = BooleanField(default=False)
    choices = ListField(required=False)

    @classmethod
    def _dfields(cls, refer):
        dynamic_fields = cls.objects.filter(refer = refer)
        ddynamic_fields = {}
        for df in dynamic_fields:
            ddynamic_fields[df.name] = eval(df.typo)()
            ddynamic_fields[df.name].name = df.name
            ddynamic_fields[df.name].max_length = df.max_length
            ddynamic_fields[df.name].min_value = df.min_value
            ddynamic_fields[df.name].max_value = df.max_value
            ddynamic_fields[df.name].required = df.required
            ddynamic_fields[df.name].choices = df.choices
        return ddynamic_fields

    def __unicode__(self):
        return u"[%s] %s: %s" % (self.refer, self.typo, self.name)