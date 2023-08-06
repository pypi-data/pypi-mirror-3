from django.template import Context, loader
from django import forms
from django.utils.translation import ugettext as _

# Taken from http://djangosnippets.org/snippets/1732/
class RenderableMixin(object):
    """
    Mixin to render forms from a predefined template
    """
    
    @property
    def form_class_name(self):
        return '.'.join([self.__module__, self.__class__.__name__.lower()])

    def as_template(self):
        """
        Renders a form from a template
        """
        self.template_name = self.__class__.__name__.lower()

        if not getattr(self, 'tpl', None):
            self.tpl = loader.get_template('form.html')

        context_dict = dict(
            non_field_errors=self.non_field_errors(),
            fields=[ forms.forms.BoundField(self, field, name) for name, field in self.fields.iteritems()],
            errors=self.errors,
            data=self.data,
            form=self,
        )

        if getattr(self, 'initial', None):
            context_dict.update(dict(initial=self.initial))
        if getattr(self, 'instance', None):
            context_dict.update(dict(instance=self.instance))
        if getattr(self, 'cleaned_data', None):
            context_dict.update(dict(cleaned_data=self.cleaned_data))

        return self.tpl.render(
            Context(context_dict)
        )
