from haystack.indexes import *
from haystack import site
from models import Thread

class ThreadIndex(RealTimeSearchIndex):
    text = CharField(document=True, use_template=True)
    participants = MultiValueField()
    last_message = DateTimeField(model_attr='latest_msg__sent_at')

    def index_queryset(self):
        return Thread.objects.all()

    def prepare_participants(self, object):
        return [p.user.pk for p in object.participants.all()]

site.register(Thread, ThreadIndex)

#from haystack import indexes
#from models import Thread
#
#class ThreadIndex(indexes.SearchIndex, indexes.Indexable):
#    text = indexes.CharField(document=True, use_template=True)
#    participants = indexes.MultiValueField()
#    last_message = indexes.DateTimeField(model_attr='latest_msg__sent_at')
#
#    def index_queryset(self):
#        return Thread.objects.all()
#
#    def prepare_participants(self, object):
#        return [p.user.pk for p in object.participants.all()]
#
#    def get_model(self):
#        return Thread
#

