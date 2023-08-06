#!/usr/bin/env python
# encoding: utf-8
"""
generator.py

Created by Luís Antônio Araújo Brito on 2012-08-28.
Copyright (c) 2012 Multmeio [design+tecnologia]. All rights reserved.
"""


from models import DynamicFields
from mongoforms.fields import MongoFormFieldGenerator
from mongoengine import *


class DynamicFieldGenerator(MongoFormFieldGenerator):
    def generate_dynamicfield(self, field_name, field, label):
        dynamic_field = DynamicFields.objects.get(refer = field.owner_document.__name__, name=field.name)
        field_wrapped = eval(dynamic_field.typo)(field)
        field_wrapped.name = field_name
        field_wrapped.label = label.capitalize()

        if hasattr(self, 'generate_%s' % field.typo.lower()):
            generator = getattr(self, 'generate_%s' % field.typo.lower())
            return generator(field_name, field_wrapped, field_wrapped.label)
        else:
            raise NotImplementedError('%s is not supported by MongoForm' % field.typo)
