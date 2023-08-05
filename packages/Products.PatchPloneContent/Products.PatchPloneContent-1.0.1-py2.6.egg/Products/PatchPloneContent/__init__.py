def addField(content_class, field):
    content_class.schema.addField(field.copy())

from plone.app.folder.folder import ATFolder
from Products.ATContentTypes.content import document, event, file, image, link, newsitem, topic

content_classes = (
    ATFolder,
    document.ATDocument,
    event.ATEvent,
    file.ATFile,
    image.ATImage,
    link.ATLink,
    newsitem.ATNewsItem,
    topic.ATTopic
)

from Products.Archetypes.ClassGen import generateMethods
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

def content_classes_add_fields(content_classes, fields):
    for content_class in content_classes:
        for field in fields:
            addField(content_class, field)
        generateMethods(content_class, content_class.schema.fields())
        folderish = content_class.meta_type == 'ATFolder'
        finalizeATCTSchema(content_class.schema, folderish=folderish)

from Products.validation import chain, config
from types import TupleType, ListType

def add_validator(field, validator, ):
    """Inserts a validator to an existing content type schema
    as first validator.  If set behind (isEmpty, V_SUFFICIENT)
    in a validation chain the validator will not be used."""
    if type(field.validators) in (TupleType, ListType):
        # Validators not initialized yet
        if type(field.validators) == TupleType:
            field.validators = (validator,) + field.validators
        else:
            field.validators.insert(0, validator)
    else:
        if len(validator) == 2:
            field.validators.insert(validator[0], mode=validator[1])
        else:
            field.validators.insertRequired(validator)
