"""
/***************************************************************************
Name                 : PostgreSQL/PostGIS util functions
Description          : Contains generic util functions for accessing the 
                       PostgreSQL/PostGIS STDM database.
Date                 : 1/April/2014
opyright             : (C) 2014 by UN-Habitat and implementing partners.
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
from PyQt4.QtCore import (
    QFile,
    QIODevice,
    QRegExp,
    QTextStream
)

from qgis.core import *

from sqlalchemy.sql.expression import text

import stdm.data
from stdm.data import STDMDb, Base
from stdm.utils import (
    getIndex,
    PLUGIN_DIR
)

_postGISTables = ["spatial_ref_sys", "str_relations", "supporting_document"]

_postGISViews = ["geometry_columns", "raster_columns", "geography_columns", "raster_overviews", "foreign_key_references"]

_pg_numeric_col_types = ["smallint", "integer", "bigint", "double precision",
                      "numeric", "decimal", "real", "smallserial", "serial", "bigserial"] 

_text_col_types = ["character varying", "text"]

#Flags for specifying data source type
VIEWS  = 2500
TABLES = 2501

def spatial_tables(exclude_views=False):
    """
    Returns a list of spatial table names in the STDM database.
    """
    t = text("select DISTINCT f_table_name from geometry_columns")
    result = _execute(t)

    sp_tables = []
    views = pg_views()

    for r in result:
        sp_table = r["f_table_name"]
        if exclude_views:
            table_index = getIndex(views, sp_table)
            if table_index == -1:
                sp_tables.append(sp_table)
        else:
            sp_tables.append(sp_table)

    return sp_tables

def pg_tables(schema="public", exclude_lookups=False):
    """
    Returns all the tables in the given schema minus the default PostGIS tables.
    Views are also excluded. See separate function for retrieving views.
    """
    t = text("SELECT table_name FROM information_schema.tables WHERE table_schema = :tschema and table_type = :tbtype " \
             "ORDER BY table_name ASC")
    result = _execute(t, tschema=schema, tbtype = "BASE TABLE")
        
    pg_tables = []
        
    for r in result:
        table_name = r["table_name"]
        
        #Remove default PostGIS tables
        table_index = getIndex(_postGISTables, table_name)
        if table_index == -1:
            if exclude_lookups:
                #Validate if table is a lookup table and if it is, then omit
                rx = QRegExp("check_*")
                rx.setPatternSyntax(QRegExp.Wildcard)
                
                if not rx.exactMatch(table_name):
                    pg_tables.append(table_name)
                    
            else:
                pg_tables.append(table_name)
            
    return pg_tables

def pg_views(schema="public"):
    """
    Returns the views in the given schema minus the default PostGIS views.
    """
    t = text("SELECT table_name FROM information_schema.tables WHERE table_schema = :tschema and table_type = :tbtype " \
             "ORDER BY table_name ASC")
    result = _execute(t, tschema=schema, tbtype="VIEW")
        
    pg_views = []
        
    for r in result:
        view_name = r["table_name"]
        #Remove default PostGIS tables
        view_index = getIndex(_postGISViews, view_name)
        if view_index == -1:
            pg_views.append(view_name)
            
    return pg_views

def pg_table_exists(table_name, include_views=True, schema="public"):
    """
    Checks whether the given table name exists in the current database
    connection.
    :param table_name: Name of the table or view. If include_views is False
    the result will always be False since views have been excluded from the
    search.
    :type table_name: str
    :param include_views: True if view names will be also be included in the
    search.
    :type include_views: bool
    :param schema: Schema to search against. Default is "public" schema.
    :type schema: str
    :return: True if the table or view (if include_views is True) exists in
    currently connected database.
    :rtype: bool
    """
    tables = pg_tables(schema=schema)
    if include_views:
        tables.extend(pg_views(schema=schema))

    if getIndex(tables, table_name) == -1:
        return False

    else:
        return True

def process_report_filter(table_name, columns, where_str="", sort_stmnt=""):
    #Process the report builder filter    
    sql = "SELECT {0} FROM {1}".format(columns, table_name)
    
    if where_str != "":
        sql += " WHERE {0} ".format(where_str)
        
    if sort_stmnt !="":
        sql += sort_stmnt
        
    t = text(sql)
    
    return _execute(t)

def table_column_names(table_name, spatial_columns=False):
    """
    Returns the column names of the given table name. 
    If 'spatialColumns' then the function will lookup for spatial columns in the given 
    table or view.
    """
    if spatial_columns:
        sql = "select f_geometry_column from geometry_columns where f_table_name = :tbname ORDER BY f_geometry_column ASC"
        column_name = "f_geometry_column"
    else:
        sql = "select column_name from information_schema.columns where table_name = :tbname ORDER BY column_name ASC"
        column_name = "column_name"
        
    t = text(sql)
    result = _execute(t, tbname=table_name)
        
    column_names = []
       
    for r in result:
        col_name = r[column_name]
        column_names.append(col_name)
           
    return column_names

def non_spatial_table_columns(table):
    """
    Returns non spatial table columns
    Uses list comprehension
    """
    all_columns = table_column_names(table)

    excluded_columns = [u'id']

    spatial_columns = table_column_names(table, True) + excluded_columns

    return [x for x in all_columns if x not in spatial_columns]

def delete_table_data(table_name, cascade=True):
    """
    Delete all the rows in the target table.
    """
    tables = pg_tables()
    table_index = getIndex(tables, table_name)
    
    if table_index != -1:
        sql = "DELETE FROM {0}".format(table_name)
        
        if cascade:
            sql += " CASCADE"
        
        t = text(sql)
        _execute(t) 

def geometry_type(table_name, spatial_column_name, schema_name="public"):
    """
    Returns a tuple of geometry type and EPSG code of the given column name in the table within the given schema.
    """
    sql = "select type,srid from geometry_columns where f_table_name = :tbname and f_geometry_column = :spcolumn and f_table_schema = :tbschema"
    t = text(sql)
    
    result = _execute(t,tbname=table_name, spcolumn=spatial_column_name, tbschema=schema_name)
        
    geomType,epsg_code = "", -1
       
    for r in result:
        geom_type = r["type"]
        epsg_code = r["srid"]
        
        break
        
    return (geom_type, epsg_code)

def unique_column_values(table_name, column_name, quote_data_types=["character varying"]):
    """
    Select unique row values in the specified column.
    Specify the data types of row values which need to be quoted. Default is varchar.
    """
    data_type = column_type(table_name, column_name)
    quote_required = getIndex(quote_data_types, data_type)
    
    sql = "SELECT DISTINCT {0} FROM {1}".format(column_name, table_name)
    t = text(sql)
    result = _execute(t)
    
    unique_vals = []
    
    for r in result:
        if r[column_name] == None:
            if quote_required == -1:
                unique_vals.append("NULL")
            else:
                unique_vals.append("''")
                
        else:
            if quote_required == -1:
                unique_vals.append(str(r[column_name]))
            else:
                unique_vals.append("'{0}'".format(str(r[column_name])))
                
    return unique_vals

def column_type(table_name, column_name):
    """
    Returns the PostgreSQL data type of the specified column.
    """
    sql = "SELECT data_type FROM information_schema.columns where table_name=:tbName AND column_name=:colName"
    t = text(sql)
    
    result = _execute(t,tbName=table_name, col_name=column_name)

    dataType = ""
    for r in result:
        data_type = r["data_type"]
        break
    return data_type

def columns_by_type(table, data_types):
    """
    :param table: Name of the database table.
    :type table: str
    :param data_types: List containing matching datatypes that should be
    retrieved from the table.
    :type data_types: list
    :return: Returns those columns of given types from the specified
    database table.
    :rtype: list
    """
    cols = []

    table_cols = table_column_names(table)
    for tc in table_cols:
        col_type = column_type(table, tc)
        type_idx = getIndex(data_types, col_type)

        if type_idx != -1:
            cols.append(tc)

    return cols

def numeric_columns(table):
    """
    :param table: Name of the database table.
    :type table: str
    :return: Returns a list of columns that are of number type such as
    integer, decimal, double etc.
    :rtype: list
    """
    return columns_by_type(table, _pg_numeric_col_types)

def numeric_varchar_columns(table, exclude_fk_columns=True):
    #Combines numeric and text column types mostly used for display columns
    num_char_types = _pg_numeric_col_types + _text_col_types

    num_char_cols = columns_by_type(table, num_char_types)

    if exclude_fk_columns:
        fk_refs = foreign_key_parent_tables(table)

        for fk in fk_refs:
            local_col = fk[0]
            col_idx = getIndex(num_char_cols, local_col)
            if col_idx != -1:
                num_char_cols.remove(local_col)

        return num_char_cols

    else:
        return num_char_cols

def qgsgeometry_from_wkbelement(wkb_element):
    """
    Convert a geoalchemy object in str or WKBElement format to the a
    QgsGeometry object.
    :return: QGIS Geometry object.
    """
    if isinstance(wkb_element, WKBElement):
        db_session = STDMDb.instance().session
        geom_wkt = db_session.scalar(wkb_element.ST_AsText())

    elif isinstance(wkb_element, str):
        split_geom = wkb_element.split(";")

        if len(split_geom) < 2:
            return None

        geom_wkt = split_geom[1]

    return QgsGeometry.fromWkt(geom_wkt)
    
def _execute(sql,**kwargs):
    """
    Execute the passed in sql statement
    """
    conn = STDMDb.instance().engine.connect()        
    result = conn.execute(sql,**kwargs)
    conn.close()
    return result

def reset_content_roles():
    roles_set = "truncate table content_base cascade;"
    _execute(text(roles_set))
    reset_sql = text(roles_set)
    _execute(reset_sql)

def delete_table_keys(table):
    #clean_delete_table(table)
    capabilities = ["Create", "Select", "Update", "Delete"]
    for action in capabilities:
        init_key = action +" "+ str(table).title()
        sql = "DELETE FROM content_roles WHERE content_base_id IN" \
              " (SELECT id FROM content_base WHERE name = '{0}');".format(init_key)
        sql2 = "DELETE FROM content_base WHERE content_base.id IN" \
               " (SELECT id FROM content_base WHERE name = '{0}');".format(init_key)
        r = text(sql)
        r2 = text(sql2)
        _execute(r)
        _execute(r2)
        Base.metadata._remove_table(table, 'public')

def safely_delete_tables(tables):
    for table in tables:
        sql = "DROP TABLE  if exists {0} CASCADE".format(table)
        _execute(text(sql))
        Base.metadata._remove_table(table, 'public')
        flush_session_activity()

def flush_session_activity():
    STDMDb.instance().session._autoflush()

def vector_layer(table_name, sql="", key="id", geom_column=""):
    """
    Returns a QgsVectorLayer based on the specified table name.
    """
    if not table_name:
        return None

    conn = stdm.data.app_dbconn
    if conn is None:
        return None

    if not geom_column:
        geom_column = None

    ds_uri = conn.to_qgs_datasource_uri()
    ds_uri.setDataSource("public", table_name, geom_column, sql, key)

    v_layer = QgsVectorLayer(ds_uri.uri(), table_name, "postgres")

    return v_layer

def foreign_key_parent_tables(table_name):
    """
    Functions that searches for foreign key references in the specified table.
    :param table_name: Name of the database table.
    :type table_name: str
    :return: A list of tuples containing the local column name, foreign table
    name and corresponding foreign column name.
    :rtype: list
    """
    #Check if the view for listing foreign key references exists
    fk_ref_view = pg_table_exists("foreign_key_references")

    #Create if it does not exist
    if not fk_ref_view:
        script_path = PLUGIN_DIR + "/scripts/foreign_key_references.sql"

        script_file = QFile(script_path)
        if script_file.exists():
            if not script_file.open(QIODevice.ReadOnly):
                return None

            reader = QTextStream(script_file)
            sql = reader.readAll()
            if sql:
                t = text(sql)
                _execute(t)

        else:
            return None

    #Fetch foreign key references
    sql = "SELECT column_name,foreign_table_name,foreign_column_name FROM " \
          "foreign_key_references where table_name=:tb_name"
    t = text(sql)
    result = _execute(t, tb_name=table_name)

    fk_refs = []

    for r in result:
        fk_ref = r["column_name"], r["foreign_table_name"],\
                 r["foreign_column_name"]
        fk_refs.append(fk_ref)

    return fk_refs

