from Products.Archetypes.Widget import RichWidget
from Products.Archetypes.Registry import registerWidget,registerPropertyType
from AccessControl import ClassSecurityInfo

class MultiParagraphWidget(RichWidget):
    _properties = RichWidget._properties.copy()
    _properties.update({
        'macro' :'@@multiparagraphwidgetmacro'
    })
    
    security = ClassSecurityInfo()    

    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False, validating=True):
        """Basic impl for form processing in a widget"""
        fname = field.getName()
        listToSort = []
        for key in form:
            if key.startswith(fname) and not (key.endswith('text_format') or key.endswith('file')):
                listToSort.append((form.get('__order__%s'%key, 'zzzzztoend'), form.get(key)))
        listToSort.sort()
        result = listToSort and zip(*listToSort)[1] or []
        return result, {}


registerWidget(MultiParagraphWidget,
               title='Muti Paragraph Select',
               description=('You can manipulate a list of kupu fields'),
               used_for=('valentine.multiparagraphfield.field.multiparagraphfield.MultiParagraphField',)
               )
