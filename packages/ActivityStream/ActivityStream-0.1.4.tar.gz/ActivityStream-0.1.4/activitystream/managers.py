import datetime
import logging
import time
from operator import itemgetter

from activitystream import base

log = logging.getLogger(__name__)

class NodeManager(base.NodeManagerBase):
    """Manages the network of connected nodes.

    Knows how to connect and disconnect nodes and serialize the graph.
    """

    def __init__(self, coll):
        self.coll = coll

    def follow(self, follower, following):
        """Create a directed edge from :class:`Node` ``follower`` to
        :class:`Node` ``following``.
        """
        self.coll.update({"node_id": follower.node_id},
                {"$addToSet": {"following": following.node_id}}, upsert=True)
        self.coll.update({"node_id": following.node_id},
                {"$addToSet": {"followers": follower.node_id}}, upsert=True)

    def unfollow(self, follower, following):
        """Destroy a directed edge from :class:`Node` ``follower`` to
        :class:`Node` ``following``.
        """
        self.coll.update({"node_id": follower.node_id},
                {"$pull": {"following": following.node_id}})
        self.coll.update({"node_id": following.node_id},
                {"$pull": {"followers": follower.node_id}})

    def is_following(self, follower, following):
        """Determine if there is a directed edge from :class:`Node`
        ``follower`` to :class:`Node` ``following``.
        """
        result = self.coll.find_one({"node_id": follower.node_id,
                "following": following.node_id})
        return result is not None

    def get_node(self, node_id):
        """Return the node for the given node_id."""
        return self.coll.find_one({"node_id": node_id})

    def get_nodes(self, node_ids):
        """Return nodes for the given node_ids."""
        return list(self.coll.find({"node_id": {"$in": node_ids}}))

    def save_node(self, node):
        """Save (upsert) a node into the collection."""
        self.coll.save(node)
        return node


class ActivityManager(base.ActivityManagerBase):
    """Serializes :class:`Activity` objects."""

    def __init__(self, activity_coll, node_manager):
        self.activity_coll = activity_coll
        self.node_manager = node_manager

    def create(self, actor, verb, obj, target=None, related_nodes=None):
        """Create and serialize an :class:`Activity`.

        Serializing includes making a copy of the activity for any node in the
        network that is connected to any node in the activity.
        """
        def obj_dict(obj):
            d = dict(activity_name=obj.activity_name,
                     activity_url=obj.activity_url)
            if obj.activity_extras:
                d['activity_extras'] = obj.activity_extras
            return d

        # Create base activity
        activity = {"actor": obj_dict(actor), "verb": verb, "obj": obj_dict(obj),
                "target": None, "published": datetime.datetime.utcnow()}
        activity["actor"]["node_id"] = actor.node_id
        if target:
            activity["target"] = obj_dict(target)

        # Figure out who needs a copy
        related_nodes = related_nodes or []
        owners = [
                node.node_id for node in [actor, obj, target] + related_nodes
                if hasattr(node, 'node_id')]

        for owner in owners:
            instance = {"node_id": owner}
            instance.update(activity)
            self.activity_coll.insert(instance)
        return activity

    def get_activities(self, nodes, since=None, sort=None, limit=0, skip=0, query=None):
        """Return all activities associated with the given nodes.

        Params:
            since (datetime) - return activities that have occured since this
                               datetime
        """
        node_ids = [node["node_id"] for node in nodes]
        q = {'node_id': {'$in': node_ids}}
        if since:
            q['published'] = {'$gt': since}
        if query:
            q.update(query)
        it = self.activity_coll.find(q, sort=sort, limit=limit, skip=skip)
        return list(it)

    def save_activities(self, activities):
        """Save (upsert) a list of activities to mongo."""
        for activity in activities:
            self.activity_coll.save(activity)

    def get_timeline(self, node_id, sort=None, limit=0, skip=0, query=None):
        """Return the timeline for node_id.

        Timeline is the already-aggregated list of activities in mongo.
        """
        q = {'owner_id': node_id}
        if query:
            q.update(query)
        it = self.activity_coll.find(q, sort=sort, limit=limit, skip=skip)
        return list(it)


class Aggregator(object):
    """Creates a timeline for a given node in the network graph."""

    def __init__(self, activity_manager, timeline_manager, node_manager):
        self.node_manager = node_manager
        self.activity_manager = activity_manager
        self.timeline_manager = timeline_manager

    def _unique_activities(self, activities):
        """Return a list of unique activities. Can't use set() b/c activities
        are dicts and therefore unhashable.
        """
        ignore_keys = ('score', 'flags', '_id', 'owner_id', 'node_id')
        unique_orig, unique_norm  = [], []
        for orig in activities:
            norm = orig.copy()
            for k in ignore_keys:
                if k in norm: del norm[k]
            if norm in unique_norm: continue
            unique_norm.append(norm)
            unique_orig.append(orig)
        return unique_orig

    def classify_activities(self, activities):
        """Return a list of activities with classfication flags added."""
        return activities

    def create_timeline(self, node_id):
        """Create, store, and return the timeline for a given node.
        """
        node = self.node_manager.get_node(node_id)
        if not node:
            log.warning('Node not found for node_id "%s". Creating...', node_id)
            node = self.node_manager.save_node(dict(node_id=node_id))
        last_timeline_aggregation = node.get('last_timeline_aggregation')
        node['last_timeline_aggregation'] = datetime.datetime.utcnow()
        # get a subset of the nodes be followed
        connections = self.filter_connections(
                self.node_manager.get_nodes(node.get('following', [])))
        # retrieve the followed nodes' activities
        activities = self.activity_manager.get_activities(connections,
                since=last_timeline_aggregation)
        # filter activities for followed nodes
        activities = self.filter_activities(activities)
        # add activities for this node
        activities += self.activity_manager.get_activities([node],
                since=last_timeline_aggregation)
        # if we don't have any activities at this point, there's nothing from
        # which to generate a timeline
        if not activities:
            return []
        # strip out _ids from activities collection, since they don't
        # apply to the timeline collection
        for activity in activities:
            activity.pop('_id', None)
        # add historical timeline activities
        activities += self.timeline_manager.get_timeline(node_id)
        # remove duplicates
        activities = self._unique_activities(activities)
        # classify and score activities
        activities = self.classify_activities(activities)
        activities = self.score_activities(activities)
        # sort and truncate the timeline
        activities = sorted(activities, key=itemgetter('score'), reverse=True)
        activities = self.truncate_timeline(activities)
        # save to this node's timeline
        for a in activities:
            a['owner_id'] = node_id
        self.timeline_manager.save_activities(activities)
        # save node to persist last_timeline_aggregation timestamp
        self.node_manager.save_node(node)
        return activities

    def needs_aggregation(self, node):
        """Return True if it's time for this node's timeline to be
        (re)aggregated).
        """
        # For now, just do an aggregation every time a timeline is requested
        return True

        # Alternative, based on time since last aggregation:
        last = node.get('last_timeline_aggregation')
        if not last: return True
        # TODO: put this time threshhold in config
        return (datetime.datetime.utcnow() - last).seconds > 60

    def get_timeline(self, node, page=0, limit=100, actor_only=False, filter_func=None):
        """Return a (paged and limited) timeline for `node`.

        `page` is zero-based (page 0 is the first page of results).

        If `actor_only` == True, timeline will be filtered to only include
        activities where `node` is the actor.

        Pass a callable to `filter_func` to arbitrarily filter activities out of the
        timeline. `filter_func` will be passed an activity, and should return True
        to keep the activity in the timeline, or False to filter it out.

        Total size of the returned timeline may be less than `limit` if:
            1. the timeline is exhausted (last page)
            2. activities are filtered out by filter_func
        """
        node_id = node.node_id
        node = self.node_manager.get_node(node_id)
        page, limit = int(page), int(limit)
        if not node or self.needs_aggregation(node):
            self.create_timeline(node_id)
        query_filter = {'actor.node_id': node_id} if actor_only else None
        timeline = self.timeline_manager.get_timeline(
                node_id, sort=[('published', -1)], skip=page*limit, limit=limit,
                query=query_filter)
        if filter_func:
            timeline = filter(filter_func, timeline)
        return timeline

    def filter_connections(self, nodes):
        """Return a subset of a node's total outbound connections (nodes he is
        following) using the algorithm of your choice.
        """
        return nodes

    def filter_activities(self, activities):
        """Return a subset of a node's activities using the algorithm of your
        choice.
        """
        return activities

    def score_activities(self, activities):
        """Return a scored list of activities. By default, newer activities
        have higher scores.
        """
        for a in activities:
            a['score'] = 1 - (1.0 / time.mktime(a['published'].timetuple()))
        return activities

    def truncate_timeline(self, activities):
        """Return a truncated timeline using the algorithm of your choice. The
        timeline activities passed in are already sorted by score, descending.
        """
        return activities
