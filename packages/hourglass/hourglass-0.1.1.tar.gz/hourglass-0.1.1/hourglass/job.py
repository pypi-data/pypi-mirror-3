import times
from rq import job

class Job(job.Job):
    @classmethod
    def create(cls, eta, func, *args, **kwargs):
        """
        Creates a new Job instance for the given function, arguments,
        and keyword arguments.
        """
        connection = kwargs.pop('connection', None)
        job = cls(connection=connection)
        job._func_name = '%s.%s' % (func.__module__, func.__name__)
        job._args, job._kwargs = args, kwargs
        job.description = job.get_call_string()
        job.eta = eta
        job.queue = None

        return job

    @classmethod
    def fetch(cls, id, connection=None):
        """
        Fetches a persisted job from its corresponding Redis key and
        instantiates it.
        """
        job = Job(id, connection=connection)
        job.refresh()
        return job

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.eta = None
        self.queue = None

    def save(self):
        """
        Persists the current job instance to its corresponding Redis key.
        """
        super(Job, self).save()

        obj = {}
        if self.eta is not None:
            obj['eta'] = times.format(self.eta, 'UTC')
        if self.queue is not None:
            obj['queue'] = self.queue
        self.connection.hmset(self.key, obj)

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
