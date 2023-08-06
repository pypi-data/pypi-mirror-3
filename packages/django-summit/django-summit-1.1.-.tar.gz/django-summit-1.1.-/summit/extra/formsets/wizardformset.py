# Ubuntu Developer Summit web application
# Copyright (C) 2008, 2009, 2010 Canonical Ltd
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

from django.forms.formsets import BaseFormSet

__all__ = (
    'WizardFormSet',
)


class WizardFormSet(BaseFormSet):
    """FormSet suitable for use in a FormWizard.

    The BaseFormSet class shipped with Django isn't iterable, so cannot be
    used inside the FormWizard class which expects to be able to iterate
    the fields of the form.

    This class provides that iteration, including the all-important management
    form.
    """

    def __iter__(self):
        for field in self.management_form:
            yield field
        for form in self.forms:
            for field in form:
                yield field
