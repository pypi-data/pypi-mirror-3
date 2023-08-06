from django import forms
from django.db import models
from django.forms import fields
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from genericm2m.models import RelatedObjectsDescriptor

__all__ = ('GenericModelForm', 'GenericModelChoiceField')


class GenericModelForm(forms.ModelForm):
    """
    This simple subclass of ModelForm fixes a couple of issues with django's
    ModelForm.

    - treat virtual fields like GenericForeignKey as normal fields, Django
      should already do that but it doesn't,
    - when setting a GenericForeignKey value, also set the object id and
      content type id fields, again Django could probably afford to do that.
    """
    def __init__(self, *args, **kwargs):
        """
        What ModelForm does, but also add virtual field values to self.initial.
        """
        super(GenericModelForm, self).__init__(*args, **kwargs)

        # do what model_to_dict doesn't
        for field in self._meta.model._meta.virtual_fields:
            self.initial[field.name] = getattr(self.instance, field.name, None)

        for name, field in self.generic_m2m_fields():
            related_objects = getattr(self.instance, name).all()
            self.initial[name] = [x.object for x in related_objects]

    def _post_clean(self):
        """
        What ModelForm does, but also set virtual field values from
        cleaned_data.
        """
        super(GenericModelForm, self)._post_clean()

        # take care of virtual fields since django doesn't
        for field in self._meta.model._meta.virtual_fields:
            value = self.cleaned_data.get(field.name, None)

            if value:
                setattr(self.instance, field.name, value)

    def generic_m2m_fields(self):
        """
        Yield name, field for each RelatedObjectsDescriptor of the model of
        this ModelForm.
        """
        for name, field in self.fields.items():
            if not isinstance(field, GenericModelMultipleChoiceField):
                continue

            model_class_attr = getattr(self._meta.model, name, None)
            if not isinstance(model_class_attr, RelatedObjectsDescriptor):
                continue

            yield name, field

    def save(self, commit=True):
        """
        What ModelForm does, but also set GFK.ct_field and GFK.fk_field if such
        a virtual field has a value.

        This should probably be done in the GFK field itself, but it's here for
        convenience until Django fixes that.
        """
        for field in self._meta.model._meta.virtual_fields:
            if isinstance(field, GenericForeignKey):
                value = self.cleaned_data.get(field.name, None)

                if not value:
                    continue

                setattr(self.instance, field.ct_field,
                        ContentType.objects.get_for_model(value))
                setattr(self.instance, field.fk_field, value.pk)

        instance = super(GenericModelForm, self).save(commit)

        def save_m2m():
            for name, field in self.generic_m2m_fields():
                model_attr = getattr(instance, name)
                selected_relations = self.cleaned_data.get(name, [])

                for related in model_attr.all():
                    if related.object not in selected_relations:
                        model_attr.remove(related)

                for related in selected_relations:
                    model_attr.connect(related)

        if hasattr(self, 'save_m2m'):
            old_m2m = self.save_m2m

            def _():
                save_m2m()
                old_m2m()
            self.save_m2m = _
        else:
            save_m2m()

        return instance
