import logging
from django.contrib import admin
from django.contrib.contenttypes import generic

from classroom.models import StaffType, Staff, Position, School 

#admin.site.register(Room)
admin.site.register(Staff)
admin.site.register(StaffType)
admin.site.register(Position)
admin.site.register(School)
