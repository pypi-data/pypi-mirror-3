# oosapy
# Copyright 11870.com
# See LICENSE for details.

"""
11870.com v2 API library for python
"""
__version__ = '0.1'
__author__ = '11870.com'
__license__ = 'Apache License, Version 2.0'

from api import API
from auth import AnonymousAuthentication, OAuthAuthentication
from error import OosApyError
from models import User, Contact, CheckIn, Activity, Area, Service,\
    SearchedService, ServiceReview, Media, Tag, List, Category, Attribute,\
    Privacy, Trusted 
