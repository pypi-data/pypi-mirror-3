from django import forms
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

class FilterMixin(object):
    filters = {}
    instance_filters = {}
    def apply_filters(self, forms=None):
        # If we didn't get a forms argument, we apply to ourself.
        if forms is None:
            forms = [self]
        # We need to apply instance filters first, as they allow us to
        # select an attribute on our instance to be the queryset, and
        # then apply a filter onto that with filters.
        for field, attr in self.instance_filters.iteritems():
            # It may be using a related attribute. person.company.units
            tokens = attr.split('.')
            
            source = None
            # See if there is any incoming data first.
            if self.data.get(tokens[0], ''):
                try:
                    source = self.instance._meta.get_field_by_name(tokens[0])[0].rel.to.objects.get(pk=self.data[tokens[0]])
                except ObjectDoesNotExist:
                    pass
            # Else, look for a match on the object we already have stored
            if not source:
                try:
                    source = getattr(self.instance, tokens[0])
                except ObjectDoesNotExist:
                    pass
            
            # Now look in form.initial
            if not source:
                source = self.initial.get(tokens[0], None)
                
            # Now, look for child attributes.
            if source:
                for segment in tokens[1:]:
                    source = getattr(source, segment)
                if forms:
                    # If the object is callable, then call it.
                    # This means we can use queryset methods (that return a queryset).
                    if callable(source):
                        source = source()
                    for form in forms:
                        if field in form.fields:
                            form.fields[field].queryset = source
        
        # We can now apply any simple filters to the queryset.
        for field, q_filter in self.filters.iteritems():
            for form in forms:
                if field in form.fields:
                    if isinstance(q_filter, Q):
                        form.fields[field].queryset = form.fields[field].queryset.filter(q_filter)
                    elif isinstance(q_filter, dict):
                        form.fields[field].queryset = form.fields[field].queryset.filter(**q_filter)
    

class FilteringForm(forms.ModelForm, FilterMixin):
    def __init__(self, *args, **kwargs):
        super(FilteringForm, self).__init__(*args, **kwargs)
        self.apply_filters()

class FilteringFormSet(forms.models.BaseInlineFormSet, FilterMixin):
    filters = {}
    instance_filters = {}
    
    def __init__(self, *args, **kwargs):
        super(FilteringFormSet, self).__init__(*args, **kwargs)
        self.apply_filters(self.forms)
    
    def _get_empty_form(self, **kwargs):
        form = super(FilteringFormSet, self)._get_empty_form(**kwargs)
        self.apply_filters([form])
        return form
    empty_form = property(_get_empty_form)
