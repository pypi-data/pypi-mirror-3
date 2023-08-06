import times
import redis
from rq.connections import get_current_connection
from rq.exceptions import NoSuchJobError, UnpickleError
from rq.queue import compact, Queue

from hourglass.job import Job

class Schedule(Queue):
    """
    A date-sorted `Queue`.

    `Schedule` uses a special subclass of `rq.Job` under the hood,
    `hourglass.job.Job` that have eta's.
    """
    # These method overrides are almost exclusively for altering the
    # Job class used (rq is not very overridable)

    def __init__(self, name='scheduled', connection=None):
        super(Schedule, self).__init__(name, connection=connection)

    @property
    def jobs(self):
        """
        Returns a list of all (valid) jobs in the queue.
        """
        def safe_fetch(job_id):
            try:
                job = Job.fetch(job_id, connection=self.connection)
            except NoSuchJobError:
                return None
            except UnpickleError:
                return None
            return job

        return compact([safe_fetch(job_id) for job_id in self.job_ids])

    def enqueue(self, eta, f, *args, **kwargs):
        """Creates a job to represent the delayed function call and enqueues
        it.

        Expects the function to call, along with the arguments and keyword
        arguments.

        The function argument `f` may be any of the following:

        * A reference to a function
        * A reference to an object's instance method
        * A string, representing the location of a function (must be
          meaningful to the import context of the workers)

        `eta` is a time in the future (in UTC) to start the job.  The
        special keyword `timeout` is reserved for `enqueue()` itself
        and it won't be passed to the actual job function.

        Another special keyword `queue` is reserved for indicating
        which queue the job should be dispatched to.
        """
        if not isinstance(f, basestring) and f.__module__ == '__main__':
            raise ValueError(
                    'Functions from the __main__ module cannot be processed '
                    'by workers.')

        # Detect explicit invocations, i.e. of the form:
        #     q.enqueue(foo, args=(1, 2), kwargs={'a': 1}, timeout=30)
        timeout = None
        queue = None
        if 'args' in kwargs or 'kwargs' in kwargs:
            assert args == (), 'Extra positional arguments cannot be used when using explicit args and kwargs.'  # noqa
            queue = kwargs.pop('queue', None)
            timeout = kwargs.pop('timeout', None)
            args = kwargs.pop('args', None)
            kwargs = kwargs.pop('kwargs', None)

        return self.enqueue_call(eta, func=f, args=args, kwargs=kwargs, timeout=timeout, queue=queue)

    def enqueue_call(self, eta, func, args=None, kwargs=None, timeout=None, queue=None):
        """
        Creates a job to represent the delayed function call and enqueues
        it.

        It is much like `.enqueue()`, except that it takes the function's args
        and kwargs as explicit arguments.  Any kwargs passed to this function
        contain options for RQ itself.
        """
        timeout = timeout or self._default_timeout
        job = Job.create(eta, func, args, kwargs, queue=queue, connection=self.connection)
        return self.enqueue_job(job, timeout=timeout)

    def enqueue_job(self, job, timeout=None, set_meta_data=True):
        """
        Enqueues a job for delayed execution.

        `eta` is a time in the future (in UTC) to start the job.  When
        the `timeout` argument is sent, it will overrides the default
        timeout value of 180 seconds.  `timeout` may either be a
        string or integer.

        If the `set_meta_data` argument is `True` (default), it will update
        the properties `origin` and `enqueued_at`.

        The job is inserted in chronological order against the
        existing jobs in the queue.
        """
        if set_meta_data:
            job.origin = self.name
            job.enqueued_at = times.now()

        if timeout:
            job.timeout = timeout
        else:
            job.timeout = 180

        job.save()

        # sort job list atomically

        with self.connection.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(self.key)

                    jobs = self.jobs
                    jobs.append(job)
                    jobs.sort(key=lambda j: j.eta)

                    pipe.multi()
                    pipe.delete(self.key)
                    pipe.rpush(self.key, *[j.id for j in jobs])
                    pipe.execute()

                    break
                except redis.WatchError:
                    continue

        return job

    def dequeue(self):
        """
        Dequeues the front-most job from this queue.

        Returns a Job instance, which can be executed or inspected.
        """
        job_id = self.pop_job_id()

        if job_id is None:
            return None
        try:
            job = Job.fetch(job_id, connection=self.connection)
        except NoSuchJobError as e:
            return self.dequeue()
        except UnpickleError as e:
            e.queue = self
            raise e

        if self.count:
            self.compact()

        return job

    def compact(self):
        # atomic compact to ensure jobs are in chronological order
        # (different that Queue.compact's FIFO policy)

        with self.connection.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(self.key)

                    job_ids = filter(
                        lambda j: pipe.exists(Job.key_for(j)),
                        pipe.lrange(self.key, 0, -1))

                    pipe.multi()
                    pipe.delete(self.key)
                    if job_ids:
                        pipe.rpush(self.key, *job_ids)
                    pipe.execute()

                    break
                except redis.WatchError:
                    continue

    def next(self):
        """
        Return the first object in the queue (the first in
        chronological order).
        """
        job_ids = self.job_ids
        if job_ids:
            try:
                return Job.fetch(job_ids[0], connection=self.connection)
            except NoSuchJobError:
                return None
        else:
            return None
