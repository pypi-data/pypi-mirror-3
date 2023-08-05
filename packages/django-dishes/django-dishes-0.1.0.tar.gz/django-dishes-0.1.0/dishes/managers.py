from datetime import datetime, timedelta, date
from django.db.models import Manager

class ActiveManager(Manager):
    def get_query_set(self):
        return super(ActiveManager, self).get_query_set().filter(publish_date__lte=date.today(), deliveries__order_deadline__gte=date.today()).distinct()
