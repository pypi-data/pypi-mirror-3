#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This module sets the taurus.core.util.Logger to be the Qt message handler"""

__all__ = ['getQtLogger', 'initTaurusQtLogger']

__docformat__ = 'restructuredtext'

from taurus.qt import Qt
import taurus.core.util

qtLogger = None

QT_LEVEL_MATCHER = {
    Qt.QtDebugMsg    : taurus.core.util.Logger.debug,
    Qt.QtWarningMsg  : taurus.core.util.Logger.warning,
    Qt.QtCriticalMsg : taurus.core.util.Logger.error,
    Qt.QtFatalMsg    : taurus.core.util.Logger.error,
    Qt.QtSystemMsg   : taurus.core.util.Logger.info
}

def getQtLogger():
    global qtLogger
    if qtLogger is None:
        qtLogger = taurus.core.util.Logger('QtLogger')
    return qtLogger
    
def qtTaurusMsgHandler(type, msg):
    global qtLogger
    if qtLogger is not None:
        caller = QT_LEVEL_MATCHER.get(type)
        caller(qtLogger, msg)

def initTaurusQtLogger():
    global qtLogger
    if not qtLogger:
        Qt.qInstallMsgHandler(qtTaurusMsgHandler)
    