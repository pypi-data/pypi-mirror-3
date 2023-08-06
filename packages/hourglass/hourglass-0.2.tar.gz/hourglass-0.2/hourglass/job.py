import times
from rq import job

class Job(job.Job):
    @classmethod
    def create(cls, eta, func, args=None, kwargs=None, connection=None, queue=None):
        """
        Creates a new Job instance for the given function, arguments,
        and keyword arguments.
        """
        job = super(Job, cls).create(func, args, kwargs, connection)
        job.eta = eta
        job.queue = queue
        return job

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.eta = None
        self.queue = None

    def save(self):
        """
        Persists the current job instance to its corresponding Redis key.
        """
        # removing our attributes so parent save() doesn't blindly
        # save them as coerced strings to redis
        eta, queue = self.eta, self.queue
        del self.eta
        del self.queue

        super(Job, self).save()

        obj = {}
        if eta is not None:
            obj['eta'] = times.format(eta, 'UTC')
        if queue is not None:
            obj['queue'] = queue
        self.connection.hmset(self.key, obj)

        # reinstate custom job attributes
        self.eta = eta
        self.queue = queue

    def refresh(self):
        """
        Overwrite the current instance's properties with the values in
        the corresponding Redis key.

        Will raise a NoSuchJobError if no corresponding Redis key exists.
        """
        super(Job, self).refresh()

        eta, queue = self.connection.hmget(self.key, ['eta', 'queue'])

        if eta is not None:
            self.eta = times.to_universal(eta)
        if queue is not None:
            self.queue = queue
