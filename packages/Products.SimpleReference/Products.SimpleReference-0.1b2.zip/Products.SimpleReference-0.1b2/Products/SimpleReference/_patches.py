'''
Created on 07.11.2011

@author: peterm
'''
from Products.SimpleAttachment import content as sa_content
from Products.SimpleReference.content import FileReference, ImageReference
from Products.SimpleReference import logger
from Products.RichDocument.content import richdocument


sa_content.file.FileReference = FileReference
sa_content.image.ImageReference = ImageReference
logger.info("patched SimpleAttachment reference types")

rd_schema = richdocument.RichDocumentSchema.copy()
rd_schema['displayImages'].widget.macro = "widget_images_references_manager"
rd_schema['displayAttachments'].widget.macro = \
    "widget_attachments_references_manager"
richdocument.RichDocument.schema = rd_schema
logger.info("patched RichDocument display macros")
