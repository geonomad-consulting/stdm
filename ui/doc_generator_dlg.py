"""
/***************************************************************************
Name                 : Document Generator By Person
Description          : Dialog that enables a user to generate documents by 
                       using person information.
Date                 : 21/May/2014 
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
from collections import OrderedDict
import sys

from PyQt4.QtGui import (
    QCursor,
    QDialog,
    QDialogButtonBox,
    QApplication,
    QProgressDialog,
    QMessageBox,
    QImageWriter,
    QFileDialog
)
from PyQt4.QtCore import (
    Qt,
    QFileInfo
)

from sqlalchemy import (
    BINARY,
    BLOB,
    Binary,
    CLOB,
    LargeBinary,
    PickleType,
    TypeDecorator,
    VARBINARY
)

from geoalchemy2 import Geometry

from stdm.composer import DocumentGenerator
from stdm.data import (
    ConfigTableReader,
    display_name,
    numeric_varchar_columns,
    ProfileException,
    _execute
)
from stdm.utils import getIndex

from .stdmdialog import DeclareMapping
from .entity_browser import ForeignKeyBrowser
from .foreign_key_mapper import ForeignKeyMapper
from .notification import NotificationBar
from .ui_doc_generator import Ui_DocumentGeneratorDialog
from .composer import TemplateDocumentSelector
from .sourcedocument import source_document_location

__all__ = ["DocumentGeneratorDialog", "EntityConfig"]

class EntityConfig(object):
    """
    Configuration class for specifying the foreign key mapper and document
    generator settings.
    """
    def __init__(self, **kwargs):
        self._title = kwargs.pop("title", "")
        self._link_field = kwargs.pop("link_field", "")
        self._display_formatters = kwargs.pop("formatters", OrderedDict())

        self._data_source = kwargs.pop("data_source", "")
        self._ds_columns = []
        self._set_ds_columns()

        self._base_model = kwargs.pop("model", None)
        self._entity_selector = kwargs.pop("entity_selector", None)
        self._expression_builder = kwargs.pop("expression_builder", False)

    def title(self):
        return self._title

    def set_title(self, title):
        self._title = title

    def _set_ds_columns(self):
        if not self._data_source:
            self._ds_columns = []

        else:
            self._ds_columns = numeric_varchar_columns(self._data_source)

    def model(self):
        return self._base_model

    def data_source(self):
        return self._data_source

    def data_source_columns(self):
        """
        Please note that these are only those columns of numeric or
        character type variants.
        """
        return self._ds_columns

    def set_data_source(self, ds):
        self._data_source = ds
        self._set_ds_columns()

    def entity_selector(self):
        return self._entity_selector

    def set_entity_selector(self, selector):
        self._entity_selector = selector

    def expression_builder(self):
        return self._expression_builder

    def set_expression_builder(self, state):
        self._expression_builder = state

    def formatters(self):
        return self._display_formatters

    def set_formatters(self, formatters):
        self._display_formatters = formatters

    def link_field(self):
        return self._link_field

    def set_link_field(self, field):
        self._link_field = field

class DocumentGeneratorDialogWrapper(object):
    """
    A utility class that fetches the tables in the active profile
    and creates the corresponding EntityConfig objects, which are then
    added to the DocumentGeneratorDialog.
    """
    def __init__(self, iface, parent=None):
        self._iface = iface
        self._doc_gen_dlg = DocumentGeneratorDialog(self._iface, parent)
        self._notif_bar = self._doc_gen_dlg.notification_bar()
        self._config_table_reader = ConfigTableReader()

        #Load entity configurations
        self._load_entity_configurations()

    def _load_entity_configurations(self):
        """
        Uses tables' information in the current profile to create the
        corresponding EntityConfig objects.
        """
        try:
            tables = self._config_table_reader.social_tenure_tables()

            for t in tables:
                #Ensure 'supporting_document' table is not in the list
                if t.find("supporting_document") == -1:
                    entity_cfg = self._entity_config_from_table(t)

                    if not entity_cfg is None:
                        self._doc_gen_dlg.add_entity_config(entity_cfg)

        except ProfileException as pe:
            self._notif_bar.clear()
            self._notif_bar.insertErrorNotification(pe.message)

    def _entity_config_from_table(self, table_name):
        """
        Creates an EntityConfig object from the table name.
        :param table_name: Name of the database table.
        :type table_name: str
        :return: Entity configuration object.
        :rtype: EntityConfig
        """
        table_display_name = display_name(table_name)
        model = DeclareMapping.instance().tableMapping(table_name)

        if model is not None:
            return EntityConfig(title=table_display_name,
                            data_source=table_name,
                            model=model,
                            expression_builder=True,
                            entity_selector=ForeignKeyBrowser)

        else:
            return None

    def dialog(self):
        """
        :return: Returns an instance of the DocumentGeneratorDialog.
        :rtype: DocumentGeneratorDialog
        """
        return self._doc_gen_dlg

    def exec_(self):
        """
        Show the dialog as a modal dialog.
        :return: DialogCode result
        :rtype: int
        """
        return self._doc_gen_dlg.exec_()

class DocumentGeneratorDialog(QDialog, Ui_DocumentGeneratorDialog):
    """
    Dialog that enables a user to generate documents by using configuration
    information for different entities.
    """
    def __init__(self, iface, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self._iface = iface
        self._docTemplatePath = ""
        self._outputFilePath = ""

        self._config_mapping = OrderedDict()
        
        self._notif_bar = NotificationBar(self.vlNotification)

        self._doc_generator = DocumentGenerator(self._iface, self)

        self._data_source = ""
        
        #Configure generate button
        generateBtn = self.buttonBox.button(QDialogButtonBox.Ok)
        if not generateBtn is None:
            generateBtn.setText(QApplication.translate("DocumentGeneratorDialog",
                                                       "Generate"))
        
        #Load supported image types
        supportedImageTypes = QImageWriter.supportedImageFormats()
        for imageType in supportedImageTypes:
            imageTypeStr = imageType.data()
            self.cboImageType.addItem(imageTypeStr)
        
        #Connect signals
        self.btnSelectTemplate.clicked.connect(self.onSelectTemplate)
        self.buttonBox.accepted.connect(self.onGenerate)
        self.chkUseOutputFolder.stateChanged.connect(self.onToggledOutputFolder)
        self.rbExpImage.toggled.connect(self.onToggleExportImage)
        self.tabWidget.currentChanged.connect(self.on_tab_index_changed)
        self.chk_template_datasource.stateChanged.connect(self.on_use_template_datasource)

    def add_entity_configuration(self, **kwargs):
        ent_config = EntityConfig(**kwargs)

        self.add_entity_config(ent_config)

    def add_entity_config(self, ent_config):
        if not self._config_mapping.get(ent_config.title(), ""):
            fk_mapper = self._create_fk_mapper(ent_config)

            self.tabWidget.addTab(fk_mapper, ent_config.title())

            self._config_mapping[ent_config.title()] = ent_config

            #Force list of column names to be loaded
            if self.tabWidget.currentIndex() != 0:
                self.tabWidget.setCurrentIndex(0)

            else:
                self.on_tab_index_changed(0)

    def on_tab_index_changed(self, index):
        if index == -1:
            return

        config = self.config(index)

        if not config is None:
            self._load_model_columns(config)

            #Set data source name
            self._data_source = config.data_source()

    def on_use_template_datasource(self, state):
        if state == Qt.Checked:
            self.tabWidget.setEnabled(False)
            self.chkUseOutputFolder.setEnabled(False)
            self.chkUseOutputFolder.setChecked(True)
            self._load_template_datasource_fields()

        elif state == Qt.Unchecked:
            self.tabWidget.setEnabled(True)
            self.chkUseOutputFolder.setEnabled(True)
            self.chkUseOutputFolder.setChecked(False)
            self.on_tab_index_changed(self.tabWidget.currentIndex())

    def notification_bar(self):
        """
        :return: Returns an instance of the notification bar.
        :rtype: NotificationBar
        """
        return self._notif_bar

    def config(self, index):
        """
        Returns the configuration for the current mapper in the tab widget.
        """
        tab_key = self.tabWidget.tabText(index)

        return self._config_mapping.get(tab_key, None)

    def current_config(self):
        """
        Returns the configuration corresponding to the current widget in the
        tab.
        """
        return self.config(self.tabWidget.currentIndex())

    def _load_model_columns(self, config):
        """
        Load model columns into the view for specifying file output name.
        Only those columns of numeric or character type variants will be
        used.
        """
        model_attr_mapping = OrderedDict()

        for c in config.data_source_columns():
            model_attr_mapping[c] = c.replace("_"," ").capitalize()

        self.lstDocNaming.load_mapping(model_attr_mapping, True)

    def _load_data_source_columns(self, ds_name):
        """
        Load the columns of a data source for use in the file naming.
        """
        table_cols = numeric_varchar_columns(ds_name)

        attr_mapping = OrderedDict()

        for c in table_cols:
            attr_mapping[c] = c.replace("_", " ").capitalize()

        self.lstDocNaming.load_mapping(attr_mapping, True)

    def _create_fk_mapper(self, config):
        fk_mapper = ForeignKeyMapper(self)
        fk_mapper.setDatabaseModel(config.model())
        fk_mapper.set_data_source_name(config.data_source())
        fk_mapper.setSupportsList(True)
        fk_mapper.setDeleteonRemove(False)
        fk_mapper.set_expression_builder(config.expression_builder())
        fk_mapper.setEntitySelector(config.entity_selector())
        fk_mapper.setNotificationBar(self._notif_bar)
        fk_mapper.setCellFormatters(config.formatters())
        fk_mapper.initialize()

        return fk_mapper
            
    def onSelectTemplate(self):
        """
        Slot raised to load the template selector dialog.
        """
        templateSelector = TemplateDocumentSelector(self)
        if templateSelector.exec_() == QDialog.Accepted:
            docName,docPath = templateSelector.documentMapping()
            
            self.lblTemplateName.setText(docName)
            self._docTemplatePath = docPath

            #Load template data source fields
            self._load_template_datasource_fields()

    def _load_template_datasource_fields(self):
        #If using template data source
        template_doc, err_msg = self._doc_generator.template_document(self._docTemplatePath)
        if template_doc is None:
            QMessageBox.critical(self, "STDM", QApplication.translate("DocumentGeneratorDialog",
                                                "Error Generating documents - %s"%(err_msg)))

            return

        composer_ds, err_msg = self._doc_generator.composer_data_source(template_doc)
        if composer_ds is None:
            QMessageBox.critical(self, "STDM", QApplication.translate("DocumentGeneratorDialog",
                                                "Error Generating documents - %s"%(err_msg)))

            return

        #Load data source columns
        self._data_source = composer_ds.name()
        self._load_data_source_columns(self._data_source)
            
    def onToggledOutputFolder(self,state):
        """
        Slot raised to enable/disable the generated output documents to be 
        written to the plugin composer output folder using the specified
        naming convention.
        """
        if state == Qt.Checked:
            self.gbDocNaming.setEnabled(True)
            
        elif state == Qt.Unchecked:
            self.gbDocNaming.setEnabled(False)
            
    def reset(self):
        """
        Clears/resets the dialog from user-defined options.
        """
        self._docTemplatePath = ""

        self._data_source = ""

        self.lblTemplateName.setText("")

        if self.tabWidget.count() > 0 and not self.chk_template_datasource.isChecked():
            self.on_tab_index_changed(0)

        if self.cboImageType.count() > 0:
            self.cboImageType.setCurrentIndex(0)
        
    def onToggleExportImage(self, state):
        """
        Slot raised to enable/disable the image formats combobox.
        """
        if state:
            self.cboImageType.setEnabled(True)

        else:
            self.cboImageType.setEnabled(False)

    def onGenerate(self):
        """
        Slot raised to initiate the certificate generation process.
        """
        self._notif_bar.clear()

        config = self.current_config()

        if config is None:
            self._notif_bar.insertErrorNotification(QApplication.translate("DocumentGeneratorDialog", \
                                            "The entity configuration could not be extracted."))

            return
        
        #Get selected records and validate
        records = self.tabWidget.currentWidget().entities()

        if self.chk_template_datasource.isChecked():
            records = self._dummy_template_records()

        if len(records) == 0:
            self._notif_bar.insertErrorNotification(QApplication.translate("DocumentGeneratorDialog", \
                                                                          "Please load at least one entity record"))

            return
        
        if not self._docTemplatePath:
            self._notif_bar.insertErrorNotification(QApplication.translate("DocumentGeneratorDialog", \
                                                                          "Please select a document template to use"))

            return
        
        documentNamingAttrs = self.lstDocNaming.selectedMappings()
        
        if self.chkUseOutputFolder.checkState() == Qt.Checked and len(documentNamingAttrs) == 0:
            self._notif_bar.insertErrorNotification(QApplication.translate("DocumentGeneratorDialog", \
                                                "Please select at least one field for naming the output document"))

            return
        
        #Set output file properties
        if self.rbExpImage.isChecked():
            outputMode = DocumentGenerator.Image
            fileExtension = self.cboImageType.currentText()
            saveAsText = "Image File"

        else:
            outputMode = DocumentGenerator.PDF 
            fileExtension = "pdf"
            saveAsText = "PDF File"
            
        #Show save file dialog if not using output folder
        if self.chkUseOutputFolder.checkState() == Qt.Unchecked:
            docDir = source_document_location()
            
            if self._outputFilePath:
                fileInfo = QFileInfo(self._outputFilePath)
                docDir = fileInfo.dir().path()
                
            self._outputFilePath = QFileDialog.getSaveFileName(self,
                                                    QApplication.translate("DocumentGeneratorDialog",
                                                    "Save Document"),
                                                    docDir,
                                                    "{0} (*.{1})".format(
                                                    QApplication.translate("DocumentGeneratorDialog",
                                                                          saveAsText),
                                                    fileExtension))
            
            if not self._outputFilePath:
                self._notif_bar.insertErrorNotification(
                    QApplication.translate("DocumentGeneratorDialog",
                                "Process aborted. No output file was specified."))

                return
            
            #Include extension in file name
            self._outputFilePath = self._outputFilePath #+ "." + fileExtension
            
        else:
            #Multiple files to be generated.
            pass

        self._doc_generator.set_link_field(config.link_field())

        self._doc_generator.clear_attr_value_formatters()

        if not self.chk_template_datasource.isChecked():
            #Apply cell formatters for naming output files
            self._doc_generator.set_attr_value_formatters(config.formatters())

        entity_field_name = "id"
        
        #Iterate through the selected records
        progressDlg = QProgressDialog(self)
        progressDlg.setMaximum(len(records))

        try:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

            for i,record in enumerate(records):
                progressDlg.setValue(i)

                if progressDlg.wasCanceled():
                    break

                #User-defined location
                if self.chkUseOutputFolder.checkState() == Qt.Unchecked:
                    status,msg = self._doc_generator.run(self._docTemplatePath, entity_field_name,
                                                  record.id, outputMode,
                                                  filePath = self._outputFilePath)

                #Output folder location using custom naming
                else:
                    status, msg = self._doc_generator.run(self._docTemplatePath, entity_field_name,
                                                    record.id, outputMode,
                                                    dataFields = documentNamingAttrs,
                                                    fileExtension = fileExtension,
                                                    data_source = self._data_source)

                if not status:
                    result = QMessageBox.warning(self,
                                                 QApplication.translate("DocumentGeneratorDialog",
                                                                        "Document Generate Error"),
                                                 msg, QMessageBox.Ignore | QMessageBox.Abort)

                    if result == QMessageBox.Abort:
                        progressDlg.close()

                        return

                else:
                    progressDlg.setValue(len(records))

            QApplication.restoreOverrideCursor()

            QMessageBox.information(self,
                QApplication.translate("DocumentGeneratorDialog",
                                       "Document Generation Complete"),
                QApplication.translate("DocumentGeneratorDialog",
                                    "Document generation has successfully completed.")
                                    )

        except Exception as ex:
            #TODO: Log stack trace
            err_msg = sys.exc_info()[1]
            QApplication.restoreOverrideCursor()

            QMessageBox.critical(self, "STDM", QApplication.translate("DocumentGeneratorDialog",
                                                                       "Error Generating documents - %s"%(err_msg)))
        #Reset UI
        self.reset()

    def _dummy_template_records(self):
        """
        This is applied when records from a template data source are to be
        used to generate the documents where no related entity will be used
        to filter matching records in the data source. The iteration of the
        data source records will be done internally within the
        DocumentGenerator class.
        """
        class _DummyRecord:
            id = 1

        return [_DummyRecord()]

    def showEvent(self, event):
        """
        Notifies if there are not entity configuration objects defined.
        :param event: Window event
        :type event: QShowEvent
        """
        if len(self._config_mapping) == 0:
            self._notif_bar.clear()

            msg = QApplication.translate("DocumentGeneratorDialog","Table "
                "configurations do not exist or have not been configured properly")
            self._notif_bar.insertErrorNotification(msg)

        return QDialog.showEvent(self, event)
