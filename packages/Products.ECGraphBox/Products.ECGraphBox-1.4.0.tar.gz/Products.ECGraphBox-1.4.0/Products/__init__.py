# -*- coding: utf-8 -*-
# $Id: __init__.py 1547 2011-04-01 07:34:35Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECAutoAssessmentBox.
#

# See http://peak.telecommunity.com/DevCenter/setuptools

#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)
