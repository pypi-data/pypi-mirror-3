# Copyright 2010-2012 Canonical Ltd.  This software is licensed under
# the GNU Lesser General Public License version 3 (see the file LICENSE).

from django.core import serializers
from django.db import models
from django.utils import simplejson
from django.db.models.fields.files import FileField


class AuditLog(models.Model):
    """
    Records of all changes made via Django admin interface.
    
    """
    username = models.CharField(max_length=255)
    user_id = models.IntegerField()
    model = models.CharField(max_length=255)
    change = models.CharField(max_length=100)
    representation = models.CharField(max_length=255)
    values = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, user, obj, change, new_object=None):
        assert change in ['create', 'update', 'delete']

        values = serializers.serialize("json", [obj])
        # json[0] is for removing outside list, this serialization is only for
        # complete separate objects, the list is unnecessary
        json = simplejson.loads(values)[0]
        if new_object:
            values_new = serializers.serialize("json", [new_object])
            json_new = simplejson.loads(values_new)[0]
            json = {'new': json_new, 'old': json}
        if change == 'delete':
            file_fields = [f for f in obj._meta.fields
                           if isinstance(f, FileField)]
            if len(file_fields) > 0:
                json['files'] = {}
                for file_field in file_fields:
                    field_name = file_field.name
                    file = getattr(obj, field_name)
                    if file.name:
                        json['files'][file.name] = file.read().encode('base64')
        values_pretty = simplejson.dumps(json, indent=2, sort_keys=True)
        return cls.objects.create(
            username=user.username,
            user_id=user.id,
            model=str(obj._meta),
            values=values_pretty,
            representation=unicode(obj),
            change=change,
        )
