from selectable.forms.widgets import AutoCompleteWidget
from django.conf import settings

__all__ = ('AutoCompleteSelect2Widget')

MEDIA_URL = settings.MEDIA_URL
STATIC_URL = getattr(settings, 'STATIC_URL', u'')
MEDIA_PREFIX = u'%sselectable_select2/' % (STATIC_URL or MEDIA_URL)

# these are the kwargs that u can pass when instantiating the widget
TRANSFERABLE_ATTRS = ('placeholder', 'initial_selection')


class SelectableSelect2MediaMixin(object):

    class Media(object):
        css = {
            'all': (u'%scss/select2.css' % MEDIA_PREFIX,)
        }
        js = (
            u'%sjs/jquery.django.admin.fix.js' % MEDIA_PREFIX,
            u'%sjs/select2.min.js' % MEDIA_PREFIX,
            u'%sjs/jquery.dj.selectable.select2.js' % MEDIA_PREFIX,
        )


class Select2BaseWidget(SelectableSelect2MediaMixin, AutoCompleteWidget):

    def __init__(self, *args, **kwargs):
        for attr in TRANSFERABLE_ATTRS:
            setattr(self, attr, kwargs.pop(attr, ''))
        super(Select2BaseWidget, self).__init__(*args, **kwargs)

    def build_attrs(self, extra_attrs=None, **kwargs):
        attrs = super(Select2BaseWidget, self).build_attrs(extra_attrs, **kwargs)

        for real_attr in TRANSFERABLE_ATTRS:
            attr = real_attr.replace('_', '-')
            attrs[u'data-' + attr] = getattr(self, real_attr)

        attrs[u'data-selectable-type'] = 'select2'
        return attrs

    def render(self, name, value, attrs=None):
        # when there is a value and no initial_selection was passed to the widget
        if value is not None and (self.initial_selection is None or self.initial_selection == ''):
            lookup = self.lookup_class()
            item = lookup.get_item(value)
            if item is not None:
                initial_selection = lookup.get_item_value(item)
                self.initial_selection = initial_selection
        return super(Select2BaseWidget, self).render(name, value, attrs)


class AutoCompleteSelect2Widget(Select2BaseWidget):
    pass
