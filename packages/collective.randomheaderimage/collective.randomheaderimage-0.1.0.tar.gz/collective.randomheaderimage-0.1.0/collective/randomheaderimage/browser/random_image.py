# -*- coding: utf-8 -*-

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
import random

class RandomImage(BrowserView):
    """Get Daily image"""
    
    def getRandomImage(self):
        """
        get the random image from a folder
        """
        pprop = getToolByName(self.context,'portal_properties')
        if pprop.site_properties.hasProperty('folder_header_images_path'):
            images_folder_path = pprop.site_properties.getProperty('folder_header_images_path')
        else:
            return ""
        if not images_folder_path:
            return ""
        root=self.context.portal_url.getPortalObject()
        image_folder=root.unrestrictedTraverse(images_folder_path,None)
        if not image_folder:
            return ""
        pc=getToolByName(self.context,'portal_catalog')
        images=pc(path='/'.join(image_folder.getPhysicalPath()),
                  portal_type="Image",
                  sort_on="getObjPositionInParent")
        if not images:
            return ""
        rnd = random.randint(0, len(images)-1)
        return 'background:url("%s") no-repeat 0 0 ; }' %images[rnd].getURL()
