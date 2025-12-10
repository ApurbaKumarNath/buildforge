# catalog/admin.py

#__________________________________________________________________________________________________________________________ (akn)

from django.contrib import admin
from .models import Component, CPU, GPU, Motherboard, RAM, Storage, PSU, Case, Review

# The simplest way to register a model.
admin.site.register(Component)
admin.site.register(CPU)
admin.site.register(GPU)
admin.site.register(Motherboard)
admin.site.register(RAM)
admin.site.register(Storage)
admin.site.register(PSU)
admin.site.register(Case)
admin.site.register(Review)

#__________________________________________________________________________________________________________________________ 