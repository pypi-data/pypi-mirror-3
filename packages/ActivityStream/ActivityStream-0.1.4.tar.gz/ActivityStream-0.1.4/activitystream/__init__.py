import threading

import pymongo

from .managers import NodeManager, ActivityManager, Aggregator

_director = None


class ActivityDirector(threading.local):
    def __init__(self, **conf):
        self.conf = conf
        if conf['activitystream.master'].startswith('mim://'):
            try:
                from ming import mim
            except ImportError, e:
                raise ImportError(str(e) + '. To use mim:// you must have the '
                        'ming package installed.')
            else:
                self.connection = mim.Connection()
        else:
            self.connection = pymongo.Connection(conf['activitystream.master'])
        self.db = self.connection[conf['activitystream.database']]
        self.activity_collection = \
                self.db[conf['activitystream.activity_collection']]
        self.timeline_collection = \
                self.db[conf['activitystream.timeline_collection']]
        self.node_collection = \
                self.db[conf['activitystream.node_collection']]
        self.node_manager = NodeManager(self.node_collection)
        self.activity_manager = ActivityManager(self.activity_collection,
                                                self.node_manager)
        self.timeline_manager = ActivityManager(self.timeline_collection,
                                                self.node_manager)
        self.aggregator = Aggregator(self.activity_manager,
                                     self.timeline_manager,
                                     self.node_manager)

    def connect(self, follower, following):
        self.node_manager.follow(follower, following)

    def disconnect(self, follower, following):
        self.node_manager.unfollow(follower, following)

    def is_connected(self, follower, following):
        return self.node_manager.is_following(follower, following)

    def create_activity(self, actor, verb, obj, target=None,
            related_nodes=None):
        return self.activity_manager.create(actor, verb, obj, target=target,
                related_nodes=related_nodes)

    def create_timeline(self, node_id):
        return self.aggregator.create_timeline(node_id)

    def get_timeline(self, *args, **kw):
        return self.aggregator.get_timeline(*args, **kw)

def configure(**conf):
    global _director
    defaults = {
            'activitystream.master': 'mongodb://127.0.0.1:27017',
            'activitystream.database': 'activitystream',
            'activitystream.activity_collection': 'activities',
            'activitystream.node_collection': 'nodes',
            'activitystream.timeline_collection': 'timelines',
    }
    defaults.update(conf)
    _director = ActivityDirector(**defaults)


def director():
    global _director
    return _director
