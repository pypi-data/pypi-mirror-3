# -*- coding: utf-8 -*-
#
# Copyright (c) 2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECGraphBox.
#
__author__ = """Fabian Fett <fett@st.ovgu.de>"""
__docformat__ = 'plaintext'

from zope.interface import Interface

class IECGraphBox(Interface):
    """Marker interface for .ECGraphBox.ECGraphBox
    """

class IECGraph(Interface):
    """Marker interface for .ECGraph.ECGraph
    """
