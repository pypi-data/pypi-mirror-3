import django

if django.VERSION[1] > 1:
    from formfield import ModelFormField
else:
    from formfield import ModelFormField as OldModelFormField
    from django.utils.functional import curry

    class ModelFormField(OldModelFormField):
        def contribute_to_class(self, cls, name):
            self.set_attributes_from_name(name)
            self.model = cls
            cls._meta.add_field(self)
            if self.choices:
                setattr(cls, 'get_%s_display' % self.name,
                        curry(cls._get_FIELD_display, field=self))
