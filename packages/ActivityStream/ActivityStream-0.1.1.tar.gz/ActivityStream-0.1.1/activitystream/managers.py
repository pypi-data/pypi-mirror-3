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
            return dict(activity_name=obj.activity_name,
                        activity_url=obj.activity_url)

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

    def get_activities(self, nodes, since=None):
        """Return all activities associated with the given nodes.

        Params:
            since (datetime) - return activities that have occured since this
                               datetime

        """
        node_ids = [node["node_id"] for node in nodes]
        q = {'node_id': {'$in': node_ids}}
        if since:
            q['published'] = {'$gt': since}
        return list(self.activity_coll.find(q))

    def save_activities(self, activities):
        """Save (upsert) a list of activities to mongo."""
        for activity in activities:
            self.activity_coll.save(activity)


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
        unique = []
        for a in activities:
            # score/flags shouldn't affect activity of comparison
            a['score'] = 0
            a['flags'] = 0
            if a in unique: continue
            unique.append(a)
        return unique

    def classify_activities(self, activities):
        """Return a list of activities with classfication flags added."""
        return activities

    def create_timeline(self, node):
        """Create, store, and return the timeline for a given node.
        """
        node_id = node.node_id
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
        # filter activies for followed nodes
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
        activities += self.timeline_manager.get_activities([node])
        # remove duplicates
        activities = self._unique_activities(activities)
        # classify and score activities
        activities = self.classify_activities(activities)
        activities = self.score_activities(activities)
        # sort and truncate the timeline
        activities = sorted(activities, key=itemgetter('score'), reverse=True)
        activities = self.truncate_timeline(activities)
        self.timeline_manager.save_activities(activities)
        return activities

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
        """Return a scored list of activities."""
        now = time.time()
        for a in activities:
            a['score'] = time.mktime(a['published'].timetuple()) / now
        return activities

    def truncate_timeline(self, activities):
        """Return a truncated timeline using the algorithm of your choice. The
        timeline activities passed in are already sorted by score, descending.
        """
        return activities
