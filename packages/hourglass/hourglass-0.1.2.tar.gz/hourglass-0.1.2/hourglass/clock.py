import time
import times
from rq import Queue

class Clock(object):
    """
    A basic clock that dispatches jobs queued up in the schedule.

    The maximum interval at which the schedule is checked is
    defined by `interval`.  The default is 1s.

    The clock's accuracy for short-term jobs is dependent on the
    `interval` property, so jobs with an `eta` delta less than
    `interval` could be missed until the next time the schedule is
    checked.
    """
    def __init__(self, queue, schedule, interval=1):
        self.queue = queue
        self.schedule = schedule
        self.interval = interval

    def tick(self):
        """
        One clock cycle.  Puts the process to sleep for the time delta
        required to the next scheduled job (if sooner than `interval`)
        or the next `tick()` call.  Example usage:

            while True:
                clock.tick()
        """
        job = self.schedule.next()

        if job:
            if job.queue:
                queue = Queue(job.queue)
            else:
                queue = self.queue

            dt = max((job.eta - times.now()).total_seconds(), 0)

            if dt < self.interval:
                time.sleep(dt)
                job = self.schedule.dequeue()
                if job:
                    queue.enqueue_job(job, timeout=job.timeout)
                    return job

        time.sleep(self.interval)
