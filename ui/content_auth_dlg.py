"""
/***************************************************************************
Name                 : Authorize Content Dialog
Description          : Provides an interface for authorizing STDM content
                       by granting/revoking permissions based on db cluster
                       roles.
Date                 : 1/July/2013 
copyright            : (C) 2013 by John Gitau
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
from PyQt4.QtCore import (
    pyqtSignal,
    Qt
)

from PyQt4.QtGui import (
    QDialog,
    QListWidget,
    QIcon,
    QWidget,
    QStandardItem,
    QStandardItemModel,
    QListWidgetItem,
    QApplication,
    QGridLayout
)

from stdm import resources_rc

from stdm.security import RoleProvider
from stdm.data import Content,Role, UsersRolesModel, STDMDb, Base
from stdm.utils import *

from ui_content_auth import Ui_frmContentAuth

class ContentListWidget(QListWidget):
    """
    List view for displaying content items based on the category they belong to
    """

    #Signals
    contentSelected = pyqtSignal(QListWidgetItem)

    def __init__(self,category,parent=None):
        QListWidget.__init__(self,parent)

        self._contentItems = []
        self._category = category

        #Initialize properties
        self.setAlternatingRowColors(True)

        self.itemActivated.connect(self.onContentClicked)
        self.itemClicked.connect(self.onContentClicked)

    def onContentClicked(self,item):
        """
        Slot activated when a content item is selected to load the roles for the specified content items.

        :param item: List widget item that was activated or clicked.
        :type item: QListWidgetItem
        """
        self.contentSelected.emit(item)

    def addContentItem(self,cnt):
        """
        :param cnt: Content item to be inserted into the view at the last position.
        :type cnt: Content
        """
        self.addItem(cnt.name)
        self._contentItems.append(cnt)

    def contentItems(self):
        """
        :return: Content items currently displayed by the widget.
        :rtype: list
        """
        return self._contentItems

    def category(self):
        """
        :return: The grouping name of the content items displayed by the list widget.
        :rtype: str
        """
        return self._category

class ContentAuthDlg(QDialog, Ui_frmContentAuth):
    '''
    Content authorization dialog
    '''
    def __init__(self,plugin):
        QDialog.__init__(self,plugin.iface.mainWindow())
        self.setupUi(self)  
        
        #Initialize the dialog
        self.initGui()

        #Mapping of content items categories and corresponding widgets
        self._cntCategories = {}
        
        #Load users
        self.loadContent()
        
        #Load Roles
        self.loadRoles()            
        
        #Reference to the currently selected STDM content item
        self.currentContent = None
        
    def initGui(self):
        '''
        Initialize GUI properties
        '''
        #Disable any action by the user in the roles view
        self.lstRoles.setEnabled(False)  
        
        #Connect signals
        self.lstRoles.activated.connect(self.onRoleSelected)
        self.lstRoles.clicked.connect(self.onRoleSelected)

    def loadContent(self):
        """
        Loads STDM content items.
        """

        self.content = Content()
        cntItems = self.content.queryObject().all()

        for cnt in cntItems:
            category = cnt.category

            #Use default category if none is specified
            if category == "":
                category = QApplication.translate("ContentAuthDlg","General")

            if not category in self._cntCategories:
                cntWidget = ContentListWidget(category)
                cntWidget.contentSelected.connect(self.onContentClicked)
                self._insertContentList(cntWidget)
                self._cntCategories[category] = cntWidget

            else:
                cntWidget = self._cntCategories[category]

            cntWidget.addContentItem(cnt)
        
    def loadRoles(self,contentname = ""):
        '''
        Loads the roles in the database cluster
        '''
        self.roleProvider = RoleProvider()
        sysRoles = self.roleProvider.GetAllRoles()
        roles = []
        
        #Load the corresponding roles for the specified content item
        cnt = Content()
        if contentname != "":
            self.currentContent = self.content.queryObject().filter(Content.name == contentname).first()
            if self.currentContent:                
                roles = [rl.name for rl in self.currentContent.roles]
        
        #Initialize model
        self.roleMappingsModel = QStandardItemModel(self)
        self.roleMappingsModel.setColumnCount(1)
        
        #Add role items into the standard item model
        for r in range(len(sysRoles)):
            role = sysRoles[r]
            if role.name != "postgres":
                roleItem = self._createNewRoleItem(role.name)
                
                #Check if the db role is in the approved for the current content item
                roleIndex = getIndex(roles,role.name)
                if roleIndex != -1:
                    roleItem.setCheckState(Qt.Checked)
                
                self.roleMappingsModel.appendRow(roleItem)
             
        self.lstRoles.setModel(self.roleMappingsModel)

    def _insertContentList(self,cntListWidget):
        """
        Insert a content list widget into the tab container. This method ensures that the widget is positioned
        correctly in the tab widget.

        :param cntListWidget: Content list widget that will be added to the tab container.
        :type cntListWidget: ContentListWidget
        """
        tab = QWidget()
        gridLayout = QGridLayout(tab)
        gridLayout.addWidget(cntListWidget, 0, 0, 1, 1)

        self.tbContentItems.addTab(tab,cntListWidget.category())
        
    def _createNewRoleItem(self,rolename):
        '''
        Creates a custom role item for use in a QStandardItemModel
        '''
        #Set icon
        icon = QIcon()
        icon.addPixmap(QPixmap(":/plugins/stdm/images/icons/roles.png"), QIcon.Normal, QIcon.Off)
        
        roleItem = QStandardItem(icon,rolename)
        roleItem.setCheckable(True)
        roleItem.setCheckState(Qt.Unchecked)
        
        return roleItem
    
    def onContentClicked(self,item):
        '''
        Slot activated when a content item is selected to load the roles for the specified content items
        '''
        self.lstRoles.setEnabled(True)
        contentName = item.text()
        self.loadRoles(contentName)
        
    def onRoleSelected(self,index):
        '''
        Slot which is called when a user checks/unchecks to add/remove a role for the 
        specified content item.
        '''
        if self.currentContent != None:
            
            item = self.roleMappingsModel.itemFromIndex(index)
            rolename = item.text()
            
            #Get role object from role name
            role = Role()
            rl = role.queryObject().filter(Role.name == rolename).first()
            
            self.blockSignals(True)            
            
            #Add role to the content item if the item is selected  or remove if it was previously checked
            if item.checkState() == Qt.Checked:    
                self.currentContent.roles.append(rl)             
                
            elif item.checkState() == Qt.Unchecked:
                self.currentContent.roles.remove(rl)
                
            self.currentContent.update()
                
            self.blockSignals(False)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
