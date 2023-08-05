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
