# The Summit Scheduler web application
# Copyright (C) 2008 - 2012 Ubuntu Community, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _

__all__ = (
    'NameField',
)

# Let South 0.7 know about this new field type
try:
    import south.v2
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^summit\.schedule\.fields\.NameField"])
except ImportError:
    pass


class NameField(models.CharField):

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.RegexField,
            'regex': r'^[a-z][a-z0-9-]*$',
            'max_length': self.max_length,
            'error_messages': {
                'invalid': _(
                u'Enter only lowercase alphanumeric characters and dashes.'),
            },
        }
        defaults.update(kwargs)
        return super(NameField, self).formfield(**defaults)
