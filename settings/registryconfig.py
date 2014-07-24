"""
/***************************************************************************
Name                 : Registry Configuration
Description          : Class for reading and writing generic KVP settings for
                        STDM stored in the registry
Date                 : 24/May/2013 
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
from PyQt4.QtCore import QSettings
from PyQt4.QtGui import QApplication

#Names of registry keys
NETWORK_DOC_RESOURCE = "NetDocumentResource"
PATHKEYS=['Config','NetDocumentResource','ComposerOutputs','ComposerTemplates']
DATABASE_LOOKUP = "LookupInit"
SYS_ADMIN_ACCOUNT = "SysAdmin"

class RegistryConfig(object):
    """
    Utility class for reading and writing STDM user settings in Windows Registry.
    """
    group_path = "STDM"

    def read(self,items):
        '''
        Get the value of the user defined items from the STDM registry tree
        '''
        userKeys = {}
        settings = QSettings()        
        settings.beginGroup("/")
        groups = settings.childGroups()

        for group in groups:
            if str(group) == self.group_path:
                for t in items:
                    tKey = self.group_path + "/" + t
                    if settings.contains(tKey):                        
                        tValue = settings.value(tKey)
                        userKeys[t] = tValue
                break

        return userKeys
    
    def write(self, settings):
        '''
        Write items in settings dictionary to the STDM registry
        '''
        uSettings = QSettings()
        stdmGroup = "/" + self.group_path

        uSettings.beginGroup(stdmGroup)

        for k,v in settings.iteritems():
            uSettings.setValue(k,v)

        uSettings.endGroup()
        uSettings.sync()

    @staticmethod
    def sys_admin():
        """
        :return: Account name of the system administrator
        :rtype: str
        """
        reg_conf = RegistryConfig()
        sys_admin = reg_conf.read([SYS_ADMIN_ACCOUNT])

        if len(sys_admin) == 0:
            msg = QApplication.translate("RegistryConfig","System admin registry key could not be found.")
            raise KeyError(msg)

        return sys_admin[SYS_ADMIN_ACCOUNT]

class QGISRegistryConfig(RegistryConfig):
    """
    Class for reading and writing QGIS-wide registry settings.
    The user has to specify the group path which contains the keys.
    """
    def __init__(self,path):
        RegistryConfig.__init__(self)
        self.group_path = path

            
        
        
        
        
        
        
        
        
        