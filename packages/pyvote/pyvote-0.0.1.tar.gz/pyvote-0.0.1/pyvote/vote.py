import redis

class AlreadyVoted(Exception):
    """
        votable object has already been voted by voter
    """

class Votable:
    """
        class to handle voting
    """
    redis = None

    def __init__(self, redis_instance = None):
        if redis_instance: self.redis = redis_instance
        else: self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)

    def up_vote(self, votable, voter):
        """
            Adds a vote to a votable object from a voter, returns True if vote was succeslfull,
            Raises AlreadyVoted if voter has voted before
        """
        if self.redis.sadd("%i" % votable, "%i" % voter):
            return True
        else:
            raise AlreadyVoted("User %i Already Voted on %i" % (voter, votable))

    def clear_vote(self, votable, voter):
        """
            Remove vote from voter to certain votable object
        """
        self.redis.srem("%i" % votable, "%i" % voter)

    def voted(self, votable, voter):
        """
            Returns True if user already voted or False otherwise
        """
        if self.redis.sismember("%i" % votable, "%i" % voter):
            return True
        else:
            return False

    def votes(self, votable):
        """
            Return the total number of votes for certain votable object
        """
        return self.redis.scard("%i" % votable)