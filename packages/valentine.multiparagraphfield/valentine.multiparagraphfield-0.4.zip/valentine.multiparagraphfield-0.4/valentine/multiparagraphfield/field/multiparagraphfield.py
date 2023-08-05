import sha #No hashlib as it's missing in Python 2.4
import random
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerField
from Products.Archetypes.Field import LinesField, ObjectField
from valentine.multiparagraphfield.utils import OrderedDict
from valentine.multiparagraphfield import MultiParagraphWidget

class MultiParagraphField(LinesField):
    
    _properties = LinesField._properties.copy()
    _properties.update({
        'widget': MultiParagraphWidget,
        })

    security  = ClassSecurityInfo()

    security.declarePublic('getHashedName')
    def getHashedName(self):
        """No hashlib as it's missing in Python 2.4"""
        return '%s_%s'%(self.getName(), sha.sha(str(random.random())).hexdigest()[:8])
    
    def moveDown(self, instance, position):
        """
        Visual order is opposite to list order. Reversed up/down.
        """
        value = list(self.get(instance))
        if position<len(value)-1:
            value[position], value[position+1] = value[position+1], value[position]
            self.set(instance, value)
    
    def moveUp(self, instance, position):
        """
        Visual order is opposite to list order. Reversed up/down.
        """
        value = list(self.get(instance))
        if position>0:
            value[position], value[position-1] = value[position-1], value[position]
            self.set(instance, value)
    

    def remove(self, instance, position):
        """
        Visual order is opposite to list order. Reversed up/down.
        """
        value = list(self.get(instance))
        if position<len(value):
            del value[position]
            self.set(instance, value)
    
    def add(self, instance, value='', position=None):
        """
        Visual order is opposite to list order. Reversed up/down.
        """
        baseValue = list(self.get(instance))
        if position is None:
            position = len(baseValue)-1
        if position<len(baseValue):
            baseValue.insert(position+1, value)
            self.set(instance, baseValue)
    

    security.declarePublic('getAllowedContentTypes')
    def getAllowedContentTypes(self, instance):
        return ['text/x-html-safe']
    
#    def getNonEmptyHTML(self):
#        """Return non-empty html content"""
#        return '<p>&nbsp;</p>'

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """
        LinesField strips the lines. I don't want to.
        """
        ObjectField.set(self, instance, value, **kwargs)
        
    def extractFromForm(self, form):
        """
        """
        fname = self.getName()
        listToSort = []
        for key in form:
            if key.startswith(fname) and not (key.endswith('text_format') or key.endswith('file')):
                listToSort.append((form.get('__order__%s'%key, 'zzzzztoend'), form.get(key)))
        listToSort.sort()
        result = listToSort and zip(*listToSort)[1] or []
        return result    
    
registerField(MultiParagraphField,
              title='MultiParagraph',
              description=('Used for storing list of paragraphs. '
                           'Paragraph may be managed separately'))
