# Copyright 2010-2012 Canonical Ltd.  This software is licensed under
# the GNU Lesser General Public License version 3 (see the file LICENSE).

from django.contrib.admin import site

from adminaudit.models import AuditLog


class AdminAuditMixin(object):

    def _flatten(self, lst):
        result = []
        for item in lst:
            if isinstance(item, list):
                result.extend(item)
            else:
                result.append(item)
        return result

    def _collect_deleted_objects(self, obj):
        result = []
        try:
            # This is for Django up to 1.2
            from django.db.models.query_utils import CollectedObjects

            seen_objs = CollectedObjects()
            obj._collect_sub_objects(seen_objs)
            for cls, subobjs in seen_objs.iteritems():
                for subobj in subobjs.values():
                    result.append(subobj)
        except ImportError:
            # Django 1.3 solution, those imports needs to be here, because
            # otherwise they will fail on Django < 1.3.
            from django.contrib.admin.util import NestedObjects
            from django.db import router

            using = router.db_for_write(obj)
            collector = NestedObjects(using=using)
            collector.collect([obj])
            result = self._flatten(collector.nested())
        return result

    def log_addition(self, request, obj, *args, **kwargs):
        AuditLog.create(request.user, obj, 'create')
        super(AdminAuditMixin, self).log_addition(request, obj, *args, **kwargs)

    def log_deletion(self, request, obj, *args, **kwargs):
        for subobj in self._collect_deleted_objects(obj):
            AuditLog.create(request.user, subobj, 'delete')
        super(AdminAuditMixin, self).log_deletion(request, obj, *args, **kwargs)

    def save_model(self, request, new_obj, form, change):
        if change:
            # This is so that we'll get the values of the object before the
            # change
            old_obj = new_obj.__class__.objects.get(pk=new_obj.pk)
            AuditLog.create(request.user, old_obj, 'update', new_object=new_obj)
        super(AdminAuditMixin, self).save_model(
            request, new_obj, form, change)


def audit_install():
    for model, model_admin in site._registry.items():
        if (model is AuditLog or isinstance(model_admin, AdminAuditMixin)):
            # Do not mingle with our own model
            continue
        site.unregister(model)
        new_model_admin = type('new_model_admin',
                               (AdminAuditMixin, model_admin.__class__),
                               model_admin.__dict__)
        site.register(model, new_model_admin)
