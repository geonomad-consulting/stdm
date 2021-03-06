"""
/***************************************************************************
Name                 : Document Generator class
Description          : Generates documents from user-defined templates.
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
import uuid

from PyQt4.QtGui import (
    QApplication,
    QImage,
    QPainter,
    QPrinter,
    QMessageBox
)
from PyQt4.QtCore import (
    QObject,
    QIODevice,
    QFile,
    QFileInfo,
    QSize,
    QSizeF,
    QRectF,
    QDir
)
from PyQt4.QtXml import QDomDocument

from qgis.core import (
    QgsComposerLabel,
    QgsComposerMap,
    QgsComposerPicture,
    QgsComposition,
    QgsFeature,
    QgsGeometry,
    QGis,
    QgsMapLayer,
    QgsMapLayerRegistry,
    QgsProject,
    QgsVectorLayer
)

from sqlalchemy.exc import ProgrammingError
from sqlalchemy.sql.expression import text
from sqlalchemy.schema import (
    Table,
    MetaData
)
from sqlalchemy import (
    Column,
    func
)
from geoalchemy2 import Geometry

from stdm.settings import RegistryConfig
from stdm.data import (
    geometryType,
    pg_table_exists,
    STDMDb,
    vector_layer
)
from stdm.ui import (
    network_document_path
)
from stdm.utils import PLUGIN_DIR

from .composer_data_source import ComposerDataSource
from .composer_wrapper import load_table_layers
from .chart_configuration import ChartConfigurationCollection
from .spatial_fields_config import SpatialFieldsConfiguration
from .photo_configuration import PhotoConfigurationCollection
from .table_configuration import TableConfigurationCollection
    
class DocumentGenerator(QObject):
    """
    Generates documents from user-defined templates.
    """
    
    #Output type enumerations
    Image = 0
    PDF = 1
    
    def __init__(self, iface, parent = None):
        QObject.__init__(self,parent)
        self._iface = iface
        self._map_renderer = self._iface.mapCanvas().mapRenderer()
        
        self._dbSession = STDMDb.instance().session
        
        self._attr_value_formatters = {}
        
        #For cleanup after document compositions have been created
        self._map_memory_layers = []

        self._table_mem_layers = []

        self._link_field = ""

        self._base_photo_table = "supporting_document"

    def link_field(self):
        """
        :return: The field name in the data source that should also exist
        in the configuration for composer items that require to use this
        reference for additional queries. This should be the name of the
        field in the child table linked through a foreign key.
        :rtype: str
        """
        return self._link_field

    def set_link_field(self, field):
        """
        :param field: Name of the link field in the data source
        :type field: str
        """
        self._link_field = field
        
    def set_attr_value_formatters(self, formattermapping):
        """
        Dictionary of attribute mappings and corresponding functions for 
        formatting the attribute value when naming an output file using 
        attribute values.
        """
        self._attr_value_formatters = formattermapping
        
    def add_attr_value_formatter(self,attributeName,formatterFunc):
        """
        Add a new attribute value formatter configuration to the collection.
        """
        self._attr_value_formatters[attributeName] = formatterFunc

    def clear_attr_value_formatters(self):
        """
        Removes all value formatters.
        """
        self._attr_value_formatters = {}

    def attr_value_formatters(self):
        """
        Returns a dictionary of attribute value formatters used by the document generators.
        """
        return self._attr_value_formatters

    def data_source_exists(self, data_source):
        """
        :param data_source: Data source object containing table/view name and
        corresponding columns.
        :type data_source: ComposerDataSource
        :return: Checks if the table or view specified in the data source exists.
        :rtype: str
        """
        return pg_table_exists(data_source.name())

    def template_document(self, path):
        """
        Reads the document template file and returns the corresponding
        QDomDocument.
        :param path: Absolute path to template file.
        :type path: str
        :return: A tuple containing the template document and error message
        where applicable
        :rtype: tuple
        """
        if not path:
            return None, QApplication.translate("DocumentGenerator",
                                                "Empty path to document template")

        if not QFile.exists(path):
            return None, QApplication.translate("DocumentGenerator",
                                                "Path to document template "
                                                "does not exist")

        template_file = QFile(path)

        if not template_file.open(QIODevice.ReadOnly):
            return None, QApplication.translate("DocumentGenerator",
                                            "Cannot read template file")

        template_doc = QDomDocument()

        if template_doc.setContent(template_file):
            return template_doc, ""

        return None, QApplication.translate("DocumentGenerator",
                                            "Cannot read document template contents")

    def composer_data_source(self, template_document):
        """
        :param template_document: Document containing document composition
        information.
        :type template_document: QDomDocument
        :return: Returns the data source defined in the template document.
        :rtype: ComposerDataSource
        """
        composer_ds = ComposerDataSource.create(template_document)

        if not self.data_source_exists(composer_ds):
            msg = QApplication.translate("DocumentGenerator",
                                             u"'{0}' data source does not exist in the database."
                                             u"\nPlease contact your database "
                                             u"administrator.".format(composer_ds.name()))

            return None, msg

        return composer_ds, ""
        
    def run(self, *args, **kwargs):
        """
        :param templatePath: The file path to the user-defined template.
        :param entityFieldName: The name of the column for the specified entity which
        must exist in the data source view or table.
        :param entityFieldValue: The value for filtering the records in the data source
        view or table.
        :param outputMode: Whether the output composition should be an image or PDF.
        :param filePath: The output file where the composition will be written to. Applies
        to single mode output generation.
        :param dataFields: List containing the field names whose values will be used to name the files.
        This is used in multiple mode configuration.
        :param fileExtension: The output file format. Used in multiple mode configuration.
        :param data_source: Name of the data source table or view whose
        row values will be used to name output files if the options has been
        specified by the user.
        """
        templatePath = args[0]
        entityFieldName = args[1]
        entityFieldValue = args[2]
        outputMode = args[3]
        filePath = kwargs.get("filePath", None)
        dataFields = kwargs.get("dataFields", [])
        fileExtension = kwargs.get("fileExtension", "")
        data_source = kwargs.get("data_source", "")
        
        templateFile = QFile(templatePath)
        
        if not templateFile.open(QIODevice.ReadOnly):
            return False, QApplication.translate("DocumentGenerator",
                                            "Cannot read template file.")

        templateDoc = QDomDocument()
        
        if templateDoc.setContent(templateFile):
            composerDS = ComposerDataSource.create(templateDoc)
            spatialFieldsConfig = SpatialFieldsConfiguration.create(templateDoc)
            composerDS.setSpatialFieldsConfig(spatialFieldsConfig)

            #Check if data source exists and return if it doesn't
            if not self.data_source_exists(composerDS):
                msg = QApplication.translate("DocumentGenerator",
                                             u"'{0}' data source does not exist in the database."
                                             u"\nPlease contact your database "
                                             u"administrator.".format(composerDS.name()))
                return False, msg

            #TODO: Need to automatically register custom configuration collections
            #Photo config collection
            ph_config_collection = PhotoConfigurationCollection.create(templateDoc)

            #Table configuration collection
            table_config_collection = TableConfigurationCollection.create(templateDoc)

            #Create chart configuration collection object
            chart_config_collection = ChartConfigurationCollection.create(templateDoc)

            #Load the layers required by the table composer items
            self._table_mem_layers = load_table_layers(table_config_collection)
            
            #Execute query
            dsTable,records = self._exec_query(composerDS.name(), entityFieldName, entityFieldValue)

            if records is None or len(records) == 0:
                return False, QApplication.translate("DocumentGenerator",
                                                    "No matching records in the database")
            
            """
            Iterate through records where a single file output will be generated for each matching record.
            """
            for rec in records:
                composition = QgsComposition(self._map_renderer)
                composition.loadFromTemplate(templateDoc)
                
                #Set value of composer items based on the corresponding db values
                for composerId in composerDS.dataFieldMappings().reverse:
                    #Use composer item id since the uuid is stripped off
                    composerItem = composition.getComposerItemById(composerId)
                    
                    if not composerItem is None:
                        fieldName = composerDS.dataFieldName(composerId)
                        fieldValue = getattr(rec,fieldName)
                        self._composeritem_value_handler(composerItem, fieldValue)

                #Extract photo information
                self._extract_photo_info(composition, ph_config_collection, rec)

                #Set table item values based on configuration information
                self._set_table_data(composition, table_config_collection, rec)

                #Refresh non-custom map composer items
                self._refresh_composer_maps(composition,
                                            spatialFieldsConfig.spatialFieldsMapping().keys())
                            
                #Create memory layers for spatial features and add them to the map
                for mapId,spfmList in spatialFieldsConfig.spatialFieldsMapping().iteritems():
                    map_item = composition.getComposerItemById(mapId)
                    
                    if not map_item is None:
                        #Clear any previous map memory layer
                        self.clear_temporary_map_layers()
                        
                        for spfm in spfmList:
                            #Use the value of the label field to name the layer
                            lbl_field = spfm.labelField()
                            spatial_field = spfm.spatialField()

                            if not spatial_field:
                                continue

                            if lbl_field:
                                if hasattr(rec, spfm.labelField()):
                                    layerName = getattr(rec, spfm.labelField())

                                else:
                                    layerName = self._random_feature_layer_name(spatial_field)
                            else:
                                layerName = self._random_feature_layer_name(spatial_field)
                            
                            #Extract the geometry using geoalchemy spatial capabilities
                            geom_value = getattr(rec, spatial_field)
                            if geom_value is None:
                                continue

                            geom_func = geom_value.ST_AsText()
                            geomWKT = self._dbSession.scalar(geom_func)

                            #Get geometry type
                            geom_type, srid = geometryType(composerDS.name(),
                                                          spatial_field)
                            
                            #Create reference layer with feature
                            ref_layer = self._build_vector_layer(layerName, geom_type, srid)

                            if ref_layer is None or not ref_layer.isValid():
                                continue
                            
                            #Add feature
                            bbox = self._add_feature_to_layer(ref_layer, geomWKT)
                            bbox.scale(spfm.zoomLevel())

                            #Workaround for zooming to single point extent
                            if ref_layer.wkbType() == QGis.WKBPoint:
                                canvas_extent = self._iface.mapCanvas().fullExtent()
                                cnt_pnt = bbox.center()
                                canvas_extent.scale(1.0/32, cnt_pnt)
                                bbox = canvas_extent

                            #Style layer based on the spatial field mapping symbol layer
                            symbol_layer = spfm.symbolLayer()
                            if not symbol_layer is None:
                                ref_layer.rendererV2().symbols()[0].changeSymbolLayer(0,spfm.symbolLayer())

                            '''
                            Add layer to map and ensure its always added at the top
                            '''
                            QgsMapLayerRegistry.instance().addMapLayer(ref_layer, False)
                            QgsProject.instance().layerTreeRoot().insertLayer(0, ref_layer)
                            self._iface.mapCanvas().setExtent(bbox)
                            self._iface.mapCanvas().refresh()

                            #Add layer to map memory layer list
                            self._map_memory_layers.append(ref_layer)

                        '''
                        Use root layer tree to get the correct ordering of layers
                        in the legend
                        '''
                        self._refresh_map_item(map_item)

                #Extract chart information and generate chart
                self._generate_charts(composition, chart_config_collection, rec)

                #Build output path and generate composition
                if not filePath is None and len(dataFields) == 0:
                    self._write_output(composition, outputMode, filePath)
                    
                elif filePath is None and len(dataFields) > 0:
                    docFileName = self._build_file_name(data_source, entityFieldName,
                                                      entityFieldValue, dataFields, fileExtension)

                    if not docFileName:
                        return (False, QApplication.translate("DocumentGenerator",
                                    "File name could not be generated from the data fields."))
                        
                    outputDir = self._composer_output_path()
                    if outputDir is None:
                        return (False, QApplication.translate("DocumentGenerator",
                            "System could not read the location of the output directory in the registry."))
                    
                    qDir = QDir()
                    if not qDir.exists(outputDir):
                        return (False, QApplication.translate("DocumentGenerator",
                                "Output directory does not exist"))
                    
                    absDocPath = u"{0}/{1}".format(outputDir, docFileName)
                    self._write_output(composition, outputMode, absDocPath)
            
            #Clear temporary layers
            self.clear_temporary_layers()
            
            return True, "Success"
        
        return False, "Document composition could not be generated"

    def _random_feature_layer_name(self, sp_field):
        return u"{0}-{1}".format(sp_field, str(uuid.uuid4())[0:8])

    def _refresh_map_item(self, map_item):
        """
        Updates the map item with the current extents and layer set in the
        map canvas.
        """
        mode = map_item.previewMode()
        if mode == QgsComposerMap.Rectangle:
            tree_layers = QgsProject.instance().layerTreeRoot().findLayers()
            layer_ids = [lyt.layerId() for lyt in tree_layers]
            map_item.setLayerSet(layer_ids)
            map_item.zoomToExtent(self._map_renderer.extent())

    def _refresh_composer_maps(self, composition, ignore_ids):
        """
        Refreshes only those map composer items whose ids are not in the list
        of 'ignore_ids'.
        """
        c_maps = composition.composerMapItems()
        for c_map in c_maps:
            if not c_map.id() in ignore_ids:
                self._refresh_map_item(c_map)

    def clear_temporary_map_layers(self):
        """
        Clears all memory map layers that were used to create the composition.
        """
        self._clear_layers(self._map_memory_layers)

    def clear_temporary_table_layers(self):
        """
        Clears all table layers for attribute tables.
        """
        self._clear_layers(self._table_mem_layers)

    def clear_temporary_layers(self):
        """
        Clears all temporary layers, both spatial and table layers.
        """
        self.clear_temporary_map_layers()
        self.clear_temporary_table_layers()

    def _clear_layers(self, layers):
        if layers is None:
            return

        try:
            layer_ids = [lyr.id() for lyr in layers]
            QgsMapLayerRegistry.instance().removeMapLayers(layer_ids)

        except RuntimeError:
            pass
    
    def _build_vector_layer(self, layer_name, geom_type, srid):
        """
        Builds a memory vector layer based on the spatial field mapping properties.
        """
        vl_geom_config = u"{0}?crs=epsg:{1!s}&field=name:string(20)&" \
                         u"index=yes".format(geom_type, srid)

        ref_layer = QgsVectorLayer(vl_geom_config, layer_name, "memory")
        
        return ref_layer

    def _load_table_layers(self, config_collection):
        """
        In order to use attribute tables in the composition, the
        corresponding vector layers need to be added to the layer
        registry. This method creates vector layers from the linked tables
        in the configuration items. This is required prior to creating the
        composition from file.
        :param config_collection: Table configuration collection built from
        the template file.
        :type config_collection: TableConfigurationCollection
        """
        table_configs = config_collection.items().values()

        v_layers = []

        for conf in table_configs:
            layer_name = conf.linked_table()
            v_layer = vector_layer(layer_name)

            if v_layer is None:
                return

            if not v_layer.isValid():
                return

            v_layers.append(v_layer)
            self._map_memory_layers.append(v_layer)

        QgsMapLayerRegistry.instance().addMapLayers(v_layers, False)

    def _set_table_data(self, composition, config_collection, record):
        #TODO: Clean up code to adopt this design.
        """
        Set table data by applying appropriate filter using information
        from the config item and the record value.
        :param composition: Map composition.
        :type composition: QgsComposition
        :param config_collection: Table configuration collection specified in
        template file.
        :type config_collection: TableConfigurationCollection
        :param record: Matching record from the result set.
        :type record: object
        """
        table_configs = config_collection.items().values()

        for conf in table_configs:
            table_handler = conf.create_handler(composition, self._exec_query)
            table_handler.set_data_source_record(record)

    def _generate_charts(self, composition, config_collection, record):
        """
        Extract chart information and use it to generate charts, which are
        exported as images then embedded in the composition as pictures.
        :param composition: Map composition
        :type composition: QgsComposition
        :param config_collection: Chart configuration collection specified
        in template file.
        :type config_collection: ChartConfigurationCollection
        :param record: Matching record from the result set.
        :type record: object
        """
        chart_configs = config_collection.items().values()

        for cc in chart_configs:
            chart_handler = cc.create_handler(composition, self._exec_query)
            chart_handler.set_data_source_record(record)

    def _extract_photo_info(self, composition, config_collection, record):
        """
        Extracts the photo information from the config using the record value
        and builds an absolute path for use by the picture composer item.
        :param composition: Map composition.
        :type composition: QgsComposition
        :param config_collection: Photo configuration collection specified in
        template file.
        :type config_collection: PhotoConfigurationCollection
        :param record: Matching record from the result set.
        :type record: object
        """
        ph_configs = config_collection.items().values()

        for conf in ph_configs:
            photo_tb = conf.linked_table()
            referenced_column = conf.source_field()
            referencing_column = conf.linked_field()

            #Get id of base photo
            alchemy_table, results = self._exec_query(photo_tb, referencing_column,
                                                      getattr(record, referenced_column, ""))

            '''
            There are no photos in the referenced table column hence insert no
            photo image
            '''
            if len(results) == 0:
                pic_item = composition.getComposerItemById(conf.item_id())

                if not pic_item is None:
                    no_photo_path = PLUGIN_DIR + "/images/icons/no_photo.png"

                    if QFile.exists(no_photo_path):
                        self._composeritem_value_handler(pic_item, no_photo_path)

                    continue

            for r in results:
                base_ph_table, doc_results = self._exec_query(self._base_photo_table,
                                                          "id", r.id)

                for dr in doc_results:
                    self._build_photo_path(composition, conf.item_id(), dr.document_type,
                                           dr.document_id, dr.filename)

                #TODO: Only interested in one photograph, should support more?
                break

    def _build_photo_path(self, composition, composer_id, doc_type, doc_id, doc_name):
        pic_item = composition.getComposerItemById(composer_id)

        if pic_item is None:
            return

        extensions = doc_name.rsplit(".", 1)
        if len(extensions) < 2:
            return

        network_ph_path = network_document_path()
        if not network_ph_path:
            return

        img_extension = extensions[1]
        abs_path = u"{0}/{1}/{2}.{3}".format(network_ph_path, doc_type,
                                             doc_id, img_extension)

        if QFile.exists(abs_path):
            self._composeritem_value_handler(pic_item, abs_path)
    
    def _add_feature_to_layer(self, vlayer, geom_wkb):
        """
        Create feature and add it to the vector layer.
        Return the extents of the geometry.
        """
        if not isinstance(vlayer, QgsVectorLayer):
            return
        
        dp = vlayer.dataProvider()
        
        feat = QgsFeature()
        g = QgsGeometry.fromWkt(geom_wkb)
        feat.setGeometry(g)
        
        dp.addFeatures([feat])
        
        vlayer.updateExtents()
        
        return g.boundingBox()
    
    def _write_output(self,composition,outputMode,filePath):
        """
        Write composition to file based on the output type (PDF or IMAGE).
        """
        if outputMode == DocumentGenerator.Image:
            self._export_composition_as_image(composition,filePath)
        
        elif outputMode == DocumentGenerator.PDF:
            self._export_composition_as_pdf(composition,filePath)
        
    def _export_composition_as_image(self, composition, file_path):
        """
        Export the composition as a raster image.
        """
        num_pages = composition.numPages()

        for p in range(num_pages):
            img = composition.printPageAsRaster(p)

            if img.isNull():
                msg = QApplication.translate("DocumentGenerator",
                                        u"Memory allocation error. Please try "
                                        u"a lower resolution or a smaller paper size.")
                raise Exception(msg)

            if p == 0:
                state = img.save(file_path)

            else:
                fi = QFileInfo(file_path)
                file_path = u"{0}/{1}_{2}.{3}".format(fi.absolutePath(),
                                                             fi.baseName(),
                    (p+1), fi.suffix())
                state = img.save(file_path)

            if not state:
                msg = QApplication.translate("DocumentGenerator",
                                        u"Error creating {0}.".format(file_path))
                raise Exception(msg)

    def _export_composition_as_pdf(self, composition, file_path):
        """
        Render the composition as a PDF file.
        """
        status = composition.exportAsPDF(file_path)
        if not status:
            msg = QApplication.translate("DocumentGenerator",
                                        u"Error creating {0}".format(file_path))

            raise Exception(msg)
    
    def _build_file_name(self, data_source, fieldName, fieldValue, data_fields,
                         fileExtension):
        """
        Build a file name based on the values of the specified data fields.
        """
        table, results = self._exec_query(data_source,fieldName, fieldValue)

        if len(results) > 0:
            rec = results[0]

            ds_values = []

            for dt in data_fields:
                f_value = getattr(rec, dt, "")
                ds_values.append(unicode(f_value))
                    
            return "_".join(ds_values) + "." + fileExtension
            
        return ""

    def _exec_query(self, dataSourceName, queryField, queryValue):
        """
        Reflects the data source then execute the query using the specified
        query parameters.
        Returns a tuple containing the reflected table and results of the query.
        """
        meta = MetaData(bind=STDMDb.instance().engine)
        dsTable = Table(dataSourceName, meta, autoload=True)

        if not queryField and not queryValue:
            #Return all the rows; this is currently limited to 100 rows
            results = self._dbSession.query(dsTable).limit(100).all()

        else:
            if isinstance(queryValue, str) or isinstance(queryValue, unicode):
                queryValue = u"'{0}'".format(queryValue)
            sql = "{0} = :qvalue".format(queryField)
            results = self._dbSession.query(dsTable).filter(sql).params(qvalue=queryValue).all()
        
        return dsTable, results
    
    def _composer_output_path(self):
        """
        Returns the directory name of the composer output directory.
        """
        regConfig = RegistryConfig()
        keyName = "ComposerOutputs"
        
        valueCollection = regConfig.read([keyName])
        
        if len(valueCollection) == 0:
            return None
        
        else:
            return valueCollection[keyName]
    
    def _composeritem_value_handler(self, composer_item, value):
        """
        Factory for setting values based on the composer item type and value.
        """
        if isinstance(composer_item,QgsComposerLabel):
            if value is None:
                composer_item.setText("")
                return
            
            if isinstance(value,int) or isinstance(value,float) or isinstance(value,long):
                composer_item.setText("%d"%(value,))
                return

            if isinstance(value, str) or isinstance(value, unicode):
                composer_item.setText(value)
                return

        #Composer picture requires the absolute file path
        elif isinstance(composer_item, QgsComposerPicture):
            if value:
                composer_item.setPictureFile(value)

            
    