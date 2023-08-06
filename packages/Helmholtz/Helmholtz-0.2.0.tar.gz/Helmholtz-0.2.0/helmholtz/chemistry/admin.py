#encoding:utf-8
from django.contrib import admin
from helmholtz.chemistry.models import Solution, QuantityOfSubstance, Substance, Product

chemistry_admin = admin.site

chemistry_admin.register(Substance)
chemistry_admin.register(Product)
chemistry_admin.register(Solution)
chemistry_admin.register(QuantityOfSubstance)
