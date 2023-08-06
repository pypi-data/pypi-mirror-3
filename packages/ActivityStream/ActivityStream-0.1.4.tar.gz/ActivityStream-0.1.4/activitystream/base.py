import abc

class NodeBase(object):
    """A node in the network."""

    @property
    def node_id(self):
        """A string that uniquely identifies this node in the network."""
        raise NotImplementedError()


class ActivityObjectBase(object):
    """A thing which participates in an Activity."""

    @property
    def activity_name(self):
        """Unicode representation of this object."""
        raise NotImplementedError()

    @property
    def activity_url(self):
        """URL of this object."""
        raise NotImplementedError()

    @property
    def activity_extras(self):
        """A BSON-serializable dict of extra stuff to store on the activity.
        """
        return {}


class ActivityBase(object):
    """Tells the story of a person performing an action on or with an object.

    Consists of an actor, a verb, an object, and optionally a target.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractproperty
    def actor(self):
        """The actor, or subject, of the Activity.

        Example: *John* posted a comment on ticket #42.

        Returns:
            :class:`NodeBase`
        """
        return None

    @abc.abstractproperty
    def verb(self):
        """The verb in the Activity.

        Example: John *posted* a comment on ticket #42.

        Returns: str
        """
        return None

    @abc.abstractproperty
    def obj(self):
        """The object of the Activity.

        Example: John posted *a comment* on ticket #42.

        Returns:
            :class:`ObjectBase`
        """
        return None

    @abc.abstractproperty
    def target(self):
        """The (optional) target of the Activity.

        Example: John posted a comment on *ticket #42*.

        Returns:
            :class:`ObjectBase`
        """
        return None

    @abc.abstractproperty
    def published(self):
        """The datetime at which the Activity was published.

        Returns:
            :class:`datetime.datetime`
        """
        return None


class NodeManagerBase(object):
    """Manages the network of connected nodes.

    Knows how to connect and disconnect nodes and serialize the graph.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def follow(self, follower, following):
        """Create a directed edge from :class:`NodeBase` ``follower`` to
        :class:`NodeBase` ``following``.
        """
        return

    @abc.abstractmethod
    def unfollow(self, follower, following):
        """Destroy a directed edge from :class:`NodeBase` ``follower`` to
        :class:`NodeBase` ``following``.
        """
        return


class ActivityManagerBase(object):
    """Serializes :class:`ActivityBase` objects."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def create(self, actor, verb, obj, target=None):
        """Create and serialize an :class:`ActivityBase`."""
        return

