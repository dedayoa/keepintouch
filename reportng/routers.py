'''
Created on Aug 25, 2016

@author: Dayo
'''

class DeliveryReportRouter(object):
    """
    A router to control all database operations on models in the
    reportng application.
    """
    def db_for_read(self, model, **hints):

        if model._meta.app_label == 'reportng':
            return 'delivery_report'
        return None

    def db_for_write(self, model, **hints):

        if model._meta.app_label == 'reportng':
            return 'delivery_report'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the reportng app is involved.
        """
        if obj1._meta.app_label == 'reportng' or obj2._meta.app_label == 'reportng':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the reportng app only appears in the 'delivery_report'
        database.
        """
        if app_label == 'reportng':
            return db == 'delivery_report'
        else:
            return False