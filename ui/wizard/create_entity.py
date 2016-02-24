# -*- coding: utf-8 -*-
"""
/***************************************************************************
Name                 : create_entity
Description          : Create an entity
Date                 : 20/January/2016
copyright            : (C) 2015 by UN-Habitat and implementing partners.
                       See the accompanying file CONTRIBUTORS.txt in the root
email                : stdm@unhabitat.org
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

from ui_entity import Ui_dlgEntity
from PyQt4.QtCore import *
from PyQt4.QtGui import (
        QDialog, 
	QApplication, 
	QMessageBox
	)

#from stdm.data import (
		#writeTable, 
		#renameTable,
		#inheritTableColumn, 
		#writeTableColumn,
		#writeLookup,
		#checktableExist,
		#ConfigTableReader, 
		#table_column_exist
		#)

#from stdm.data.config_utils import setUniversalCode

from stdm.data.configuration.entity import *
from stdm.data.configuration.db_items import DbItem

class EntityEditor(QDialog, Ui_dlgEntity):
    def __init__(self, parent, profile, entity=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

	self.profile = profile
	self.form_parent = parent
        self.entity = entity

        self.initGui()

    def initGui(self):
        self.edtTable.setFocus()
	self.setTabOrder(self.edtTable, self.edtDesc)
        if self.entity:
            self.edtTable.setText(self.entity.short_name)
            self.edtDesc.setText(self.entity.description)
            self.cbSupportDoc.setCheckState( \
                    self.bool_to_check(self.entity.supports_documents))
       
    def setLookupTable(self):
        '''def add lookup table'''
        tableName = self.format_table_name(unicode(self.edtTable.text()))
        if str(tableName).startswith("check"):
            self.table = tableName
        if not str(tableName).startswith("check"):
            self.table = 'check_'+tableName
        attrib={}
        tableDesc = str(self.edtDesc.text())
        attrib['name'] = self.table
        attrib['fullname'] = tableDesc
        
    def format_table_name(self, name):
	formatted_name = name.strip()
	formatted_name = formatted_name.replace(' ', "_")
	return formatted_name.lower()
    
    def add_entity(self):
        entity_name = unicode(self.edtTable.text())

        if self.entity is None:
            if self.profile.entities.has_key(entity_name):
                # if entity exist and action is "DROP", replace it
                entity = self.profile.entity(entity_name)
                if entity.action <> DbItem.DROP:
                    self.error_message(QApplication.translate("EntityEditor","Entity with the same name already exist!"))
                    return False

            entity = self.profile.create_entity(entity_name, entity_factory,
                    supports_documents=self.support_doc())
            entity.description = self.edtDesc.text()
            entity.column_added.connect(self.form_parent.add_column_item)
            entity.column_removed.connect(self.form_parent.delete_column_item)
            self.profile.add_entity(entity)
            return True
        else:
            # editing
            self.profile.remove_entity(entity_name)
            entity = self.profile.create_entity(entity_name, entity_factory,
                    supports_documents=self.support_doc())
            entity.description = self.edtDesc.text()
            entity.column_added.connect(self.form_parent.add_column_item)
            entity.column_removed.connect(self.form_parent.delete_column_item)
            self.profile.add_entity(entity)
            return True
            

    def support_doc(self):
        if self.cbSupportDoc.checkState() == Qt.Checked:
            return True
        else:
            return False

    def bool_to_check(self, state):
        if state:
            return Qt.Checked
        else:
            return Qt.Unchecked
	    
    def accept(self):
        if self.edtTable.text()=='':
            self.error_message(QApplication.translate("EntityEditor","Entity name is not given"))
            return

        if self.add_entity():
            self.done(1)
        else:
            return

    def reject(self):
        self.done(0)
    
    def error_message(self, Message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("STDM")
        msg.setText(Message)
        msg.exec_()  