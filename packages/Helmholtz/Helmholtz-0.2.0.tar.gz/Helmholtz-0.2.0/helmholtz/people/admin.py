#encoding:utf-8
from django.contrib import admin
from helmholtz.people.models import Address, EMail, Phone, Fax, WebSite, Researcher, Supplier, ScientificStructure, PositionType, Position

community_admin = admin.site

community_admin.register(Address)
community_admin.register(EMail)
community_admin.register(Phone)
community_admin.register(Fax)
community_admin.register(WebSite)
community_admin.register(ScientificStructure)
community_admin.register(Researcher)
community_admin.register(Supplier)
community_admin.register(PositionType)
community_admin.register(Position)
