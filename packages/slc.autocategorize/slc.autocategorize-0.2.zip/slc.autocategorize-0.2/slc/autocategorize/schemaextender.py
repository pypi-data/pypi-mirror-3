from zope.interface import implements

from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.field import ExtensionField

from Products.Archetypes import atapi
from Products.CMFPlone import PloneMessageFactory as _

from interfaces import IAutocategorizeLayer

class ExtendedBooleanField(ExtensionField, atapi.BooleanField):
    """ """

class SchemaExtender(object):
    """ Extend a folder to add the 'Auto-categorize checkbox' """
    implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)

    layer = IAutocategorizeLayer

    def __init__(self, context):
        self.context = context

    _fields = [
            ExtendedBooleanField('autoCategorizeNewContent',
                schemata='categorization',
                languageIndependent=True,
                accessor='autoCategorizeNewContent',
                widget=atapi.BooleanWidget(
                    visible={'edit': 'visible', 'view': 'invisible'},
                    label = _(
                        u'label_auto_categorize_new_content', 
                        default=u'Automatically categorize content newly '
                        'created inside this folder?',
                    ),
                    description=_(
                        u'description_auto_categorize_new_content', 
                        default=u"Select this option if you want  "
                        "content created inside this folder to automatically "
                        "acquire the same categories. "
                    ),
                ),
            ),
            ExtendedBooleanField('recursiveAutoCategorization',
                schemata='categorization',
                languageIndependent=True,
                accessor='recursiveAutoCategorization',
                widget=atapi.BooleanWidget(
                    visible={'edit': 'visible', 'view': 'invisible'},
                    label = _(
                        u'label_recursive_autocategorization', 
                        default=u'Apply the automatic categorization '
                        'recursively.'
                    ),
                    description=_(
                        u'description_recursive_autocategorization', 
                        default=u"Select this option if you want  "
                        "the objects created inside subfolders of this folder "
                        " to also receive these categories. <br/>"
                        "NOTE: This option is only applicable if the previous "
                        "checkbox is enabled. <br/>"
                        "IMPORTANT: Be aware that this option can considerably "
                        "increase the amount of time it takes to add objects!"
                    ),
                ),
            ),
            ]

    def getFields(self):
        return self._fields

    def getOrder(self, original):
        for fs in original.keys():
            if "autoCategorizeNewContent" in original[fs]:
                original[fs].remove("autoCategorizeNewContent")

            if "recursiveAutoCategorization" in original[fs]:
                original[fs].remove("recursiveAutoCategorization")
        
            if "subject" in original[fs]:
                ls = original[fs]
                ls.insert(ls.index('subject')+1, 'autoCategorizeNewContent')
                ls.insert(ls.index('subject')+2, 'recursiveAutoCategorization')
                original[fs] = ls

        return original

