from django.db import models
from datetime import datetime

class EntryManager(models.Manager):

    def active(self):
        """
        Retrieves all active entries which have been published.
        
        """
        now = datetime.now()
        return self.get_query_set().filter(
                published_on__lte=now,
                published=True)

    def live(self, user=None):
        """Retrieves all live entries"""

        qs = self.active()

        if user is not None and user.is_superuser:
            # superusers get to see all entries 
            return qs
        else:
            # only show live entries to regular users
            return qs.filter(published=True)

class TeacherManager(models.Manager):
    def get_query_set(self):
        return super(TeacherManager, self).get_query_set().filter(type__title='Teacher').filter(active=True)

class StaffManager(models.Manager):
    def get_query_set(self):
        return super(StaffManager, self).get_query_set().filter(type__title='Staff').filter(active=True)

class ConsultantManager(models.Manager):
    def get_query_set(self):
        return super(ConsultantManager, self).get_query_set().filter(type__title='Consultant').filter(active=True)

class ActiveManager(models.Manager):
    def get_query_set(self):
        return super(ActiveManager, self).get_query_set().filter(active=True).order_by('name')
