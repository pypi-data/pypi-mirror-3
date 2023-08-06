import times
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
                job = Job.fetch(job_id)
            except NoSuchJobError:
                return None
            except UnpickleError:
                return None
            return job

        return compact([safe_fetch(job_id) for job_id in self.job_ids])

    def enqueue(self, eta, f, *args, **kwargs):
        """
        Creates a job to represent the delayed function call and enqueues
        it.

        Expects the function to call, along with the arguments and keyword
        arguments.

        `eta` is a time in the future (in UTC) to start the job.  The
        special keyword `timeout` is reserved for `enqueue()` itself
        and it won't be passed to the actual job function.

        Another special keyword `queue` is reserved for indicating
        which queue the job should be dispatched to.
        """
        if f.__module__ == '__main__':
            raise ValueError(
                    'Functions from the __main__ module cannot be processed '
                    'by workers.')

        queue = kwargs.pop('queue', None)
        timeout = kwargs.pop('timeout', None)
        job = Job.create(eta, f, *args, connection=self.connection, **kwargs)
        job.queue = queue
        return self.enqueue_job(eta, job, timeout=timeout)

    def enqueue_job(self, eta, job, timeout=None, set_meta_data=True):
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
        if self.count:
            self.compact()

        job.eta = eta

        if set_meta_data:
            job.origin = self.name
            job.enqueued_at = times.now()

        if timeout:
            job.timeout = timeout
        else:
            job.timeout = 180

        job.save()

        jobs = self.jobs
        jobs.append(job)
        jobs.sort(key=lambda j: j.eta)

        pipe = self.connection.pipeline()
        pipe.delete(self.key)
        map(lambda j: pipe.rpush(self.key, j.id), jobs)
        pipe.execute()

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

    def next(self):
        """
        Return the first object in the queue (the first in
        chronological order).
        """
        if self.count:
            try:
                return Job.fetch(self.job_ids[0], connection=self.connection)
            except NoSuchJobError:
                return None
        else:
            return None
