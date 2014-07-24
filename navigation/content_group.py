"""
/***************************************************************************
Name                 : ContentGroup
Description          : Groups related content items together
Date                 : 29/April/2014
copyright            : (C) 2014 by John Gitau
email                : gkahiu@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtGui import (
    QApplication,
    QAction
)
from PyQt4.QtCore import pyqtSignal,QObject

from stdm.security import Authorizer, SecurityException
from stdm.data import (
    Content,
    initLookups,
    Role,
    STDMDb,
    Base,
    PseudoEnum,
    app_dbconn
)
from stdm.settings import RegistryConfig
from stdm.utils import randomCodeGenerator,HashableMixin,getIndex
from sqlalchemy import Table

__all__ = ["ContentGroup,TableContentGroup","ContentItem"]

class ContentItem(object):
    """
    Module that needs to be registered in the database with the corresponding
    permissions set.
    """
    def __init__(self,content,permission,container_item=None):
        """
        :param content: A generic content item describing its attributes.
        :type content: Content

        :param permission: A class defining the permission set of the content.
        This must be a subclass of PseudoEnum object.
        :type permission: PseudoEnum

        :param container_item: Instance of Qt widget that will link this content item
        to the UI.
        """
        self._content = content
        self._permission = permission
        self._container_item = container_item

        #Assert if there is an existing copy of the content
        if self._content.code != "":
            cnt = Content()
            queryOj = cnt.queryObject().filter(Content.code == self._content.code).one()

        else:
            msg = QApplication.translate("ContentItem","Content code cannot be empty")
            raise AttributeError(msg)

        db_mappings = self._permission.model_mappings()

        if len(db_mappings) > 0:
            self._content.registered_permissions = db_mappings

    @staticmethod
    def content_from_qaction(self,qaction,code="",category=""):
        """
        :param qaction: A QAction object.
        :type qaction: QAction

        :param code: Unique identifier for the content.
        :type code: str

        :param category: The logical grouping of the content. By default if not specified,
        then the content will be under the 'General' category.
        :type category: str

        :returns: SQLAlchemy content object initialized with the corresponding arg values.
        :rtype: Content
        """
        cnt = Content()
        cnt.name = qaction.text()

        if code != "": cnt.code = code

        if category != "": cnt.category = category

        return cnt

    def set_container_item(self,container_item):
        """
        Set the Qt object that is to be associated with the content item.

        :param container_item: Instance of Qt object.
        :type container_item: QObject
        """
        self._containerItem = container_item

    def containerItem(self):
        """
        :returns: Returns an instance of a ContainerItem associated with this group.
        :rtype: QObject
        """
        return self._containerItem

    def register(self):
        """
        Register the content to the database repository.
        """
        username = data.app_dbconn.User.UserName
        sys_admin_account = RegistryConfig.sys_admin()

        if sys_admin_account == "":
            msg = QApplication.translate("ContentItem","System administrator account is empty.")
            raise RuntimeError(msg)

        if username == sys_admin_account:
            #Check if the content exists
            query_cnt = Content()
            cn = query_cnt.queryObject().filter(Content.code == self._content.code).first()

            if cn == None:
                self._content.save()

                #Grant permissions to the sys_admin_account
                rl = Role()
                query_role = rl.queryObject().filter(Role.name == sys_admin_account).first()

                if query_role == None:
                    rl.name = sys_admin_account
                    rl.permissions = self._content.registered_permissions
                    rl.save()

                else:
                    query_role.permissions.append(self._content.registered_permissions)
                    query_role.update()

            #Initialize lookup values
            initLookups()

class ContentGroup(QObject,HashableMixin):
    """
    Groups related content items together.
    """
    contentAuthorized = pyqtSignal(Content)
    registeredItems = []
    
    def  __init__(self,username,containerItem = None,parent = None):
        QObject.__init__(self,parent)
        HashableMixin.__init__(self)
        self._username = username
        self._contentItems = []
        self._authorizer = Authorizer(self._username)
        self._containerItem = containerItem
        
    def hasPermission(self,content):
        """
        Checks whether the currently logged in user has permissions to access
        the given content item.
        """
        return self._authorizer.CheckAccess(content.code)
    
    @staticmethod
    def contentItemFromQAction(qAction):
        """
        Creates a Content object from a QAction object.
        """
        cnt = Content()
        cnt.name = qAction.text()
        
        return cnt
    
    def contentItems(self):
        """
        Returns a list of content items in the group.
        """
        return self._contentItems
    
    def addContent(self,name,code):
        """
        Create a new Content item and add it to the collection.
        """
        cnt = Content()
        cnt.name = name
        cnt.code = code
        
        self._contentItems.append(cnt)
        
    def addContentItems(self,contents):
        """
        Append list of content items to the group's collection.
        """
        self._contentItems.extend(contents)
        
    def addContentItem(self,content):
        """
        Adds a Content instance to the collection.
        """
        self._contentItems.append(content)
    
    def setContainerItem(self,containerItem):
        """
        ContainerItem can be a QAction, QListWidgetItem, etc. that can be associated with the group.
        """
        self._containerItem = containerItem
        
    def containerItem(self):
        """
        Returns an instance of a ContainerItem associated with this group.
        """
        return self._containerItem
    
    def checkContentAccess(self):
        """
        Asserts whether each content item(s) in the group has access permissions.
        For each item that has permission then a signal is raised containing the
        Content item as an argument.
        Those items which have been granted permission will be returned in a list.
        """
        allowedContent = []
        
        for c in self.contentItems():
            hasPerm = self.hasPermission(c)
            if hasPerm:
                allowedContent.append(c)
                self.contentAuthorized.emit(c)
            
        return allowedContent
    
    def register(self):
        """
        Registers the content items into the database. Registration only works for a 
        postgres user account.
        """
        return

        pg_account = "postgres"   
        
        if self._username == pg_account:
            for c in self.contentItems():
                if isinstance(c,Content):
                    cnt = Content()
                    qo = cnt.queryObject()
                    cn = qo.filter(Content.code == c.code).first()
                    
                    #If content not found then add
                    if cn == None:                            
                        #Check if the 'postgres' role is defined, if not then create one
                        rl = Role()
                        roleQuery = rl.queryObject()
                        role = roleQuery.filter(Role.name == pg_account).first()
                        
                        if role == None:
                            rl.name = pg_account
                            rl.contents = [c]
                            rl.save()                     
                        else:
                            existingContents = role.contents
                            #Append new content to existing 
                            existingContents.append(c)
                            role.contents = existingContents
                            role.update()     
                    
            #Initialize lookup values
            initLookups()

class ViewContentGroup(ContentGroup):
    """
    Groups operations for a database view. In most databases, a view only supports read operations.
    """
    read_op = QApplication.translate("DatabaseContentGroup", "Select")

    def __init__(self,username,groupName,action=None):
        ContentGroup.__init__(self,username,action)
        self._groupName = groupName
        self._createReadContentItem()

    def readContentItem(self):
        """
        Returns Read/Select content item.
        """
        return self._readCnt

    def canRead(self):
        """
        Returns whether the current user has read permissions.
        """
        return self.hasPermission(self._readCnt)

    def _createReadContentItem(self):
        """
        Create the read/select content item.
        """
        self._readCnt = Content()
        self._readCnt.name = self._buildName(self.read_op)
        self.addContentItem(self._readCnt)

    def _buildName(self,contentName):
        """
        Appends group name to the content name
        """
        return "{0} {1}".format(contentName, self._groupName)

class TableContentGroup(ViewContentGroup):
    """
    For grouping CRUD operations for a specific model corresponding
    to a given database table.
    """
    create_op = QApplication.translate("DatabaseContentGroup", "Create")
    update_op = QApplication.translate("DatabaseContentGroup", "Update")
    delete_op = QApplication.translate("DatabaseContentGroup", "Delete")
    
    def __init__(self,username,groupName,action = None):
        ViewContentGroup.__init__(self,username,groupName,action)
        self._createDbOpContent()
        
    def _createDbOpContent(self):
        """
        Create content for database operations.
        The code for each content needs to be set by the caller.
        """
        self._createCnt = Content()
        self._createCnt.name = self._buildName(self.create_op)
        self.addContentItem(self._createCnt)

        self._updateCnt = Content()
        self._updateCnt.name = self._buildName(self.update_op)
        self.addContentItem(self._updateCnt)
        
        self._deleteCnt = Content()
        self._deleteCnt.name = self._buildName(self.delete_op)
        self.addContentItem(self._deleteCnt)
        
    def createContentItem(self):
        """
        Returns Create content item.
        """
        return self._createCnt
    
    def updateContentItem(self):
        """
        Returns Update content item.
        """
        return self._updateCnt
    
    def deleteContentItem(self):
        """
        Returns Delete content item.
        """
        return self._deleteCnt
    
    def canCreate(self):
        """
        Returns whether the current user has create permissions.
        """
        return self.hasPermission(self._createCnt)
    
    def canUpdate(self):
        """
        Returns whether the current user has update permissions.
        """
        return self.hasPermission(self._updateCnt)
    
    def canDelete(self):
        """
        Returns whether the current user has delete permissions.
        """
        return self.hasPermission(self._deleteCnt)

class LayersContentGroup(ContentGroup):
    """
    Content group for registering spatial layers. This group is not associated with any QAction.
    """
    def __init__(self,username):
        ContentGroup.__init__(self,username,None)
        self._spatialContentGroups = []
        self._createLayerContentItems()

    def _createLayerContentItems(self):
        """
        Create content items for each layer item in the database.
        """
        from stdm.data import  spatial_tables,pg_views

        spTables = spatial_tables()
        views = pg_views()

        for spTable in spTables:
            #Check if the table is a view
            viewIndex = getIndex(views,spTable)
            if viewIndex == -1: #It is a table
                layerContentGroup = TableContentGroup(self._username,spTable)
            else:
                layerContentGroup = ViewContentGroup(self._username,spTable)

            self._spatialContentGroups.append(layerContentGroup)

    def contentGroups(self):
        """
        :return: List of registered content groups for table and view-based layers.
        :rtype: list
        """
        return self._spatialContentGroups

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        