from Products.Archetypes.Widget import StringWidget
from Products.Archetypes.Registry import registerWidget
from collective.flattr import flattrMessageFactory as _

class FlattrThingWidget(StringWidget):
    _properties = StringWidget._properties.copy()
    _properties.update({
            'macro': 'flattrthing',
            'helper_js': ('flattrthing.js',),
        })

registerWidget(FlattrThingWidget,
                title=_(u'Flattr Thing'),
                description=_(u'Allows to create or select a flattr thing'),
                used_for=('Products.Archetypes.Field.StringField'))
