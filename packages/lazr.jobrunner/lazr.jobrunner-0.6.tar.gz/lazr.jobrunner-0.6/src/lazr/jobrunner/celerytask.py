# Copyright 2012 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.jobrunner
#
# lazr.jobrunner is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.jobrunner is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.jobrunner. If not, see <http://www.gnu.org/licenses/>.

__metaclass__ = type


from functools import partial
from socket import timeout

from celery.task import Task
from kombu import Consumer, Exchange, Queue

from lazr.jobrunner.jobrunner import (
    JobRunner,
    LeaseHeld,
    memory_limit,
    )


class RunJob(Task):

    abstract = True

    oops_config = None

    def getJobRunner(self):
        return JobRunner(oops_config=self.oops_config)

    def run(self, job_id):
        job = self.job_source.get(job_id)
        try:
            job.acquireLease()
        except LeaseHeld:
            return
        runner = self.getJobRunner()
        with memory_limit(self.job_source.memory_limit):
            runner.runJobHandleError(job, self.fallbackToSlowerLane(job_id))

    def fallbackToSlowerLane(self, job_id):
        """Return a callable that is called by the job runner when
        a request times out.

        The callable should try to put the job into another queue. If
        such a queue is not defined, return None.
        """
        fallback_queue = self.app.conf.get('FALLBACK_QUEUE')
        if fallback_queue is None:
            return None
        return partial(self.reQueue, job_id, fallback_queue)

    def reQueue(self, job_id, fallback_queue):
        self.apply_async(args=(job_id, ), queue=fallback_queue)


def list_queued(app, queue_names):
    """List the queued messages as body/message tuples for a given app.

    :param app: The app to list queues for (affects backend, Queue type,
        etc.).
    :param queue_names: Names of the queues to list.
    """
    listings = []

    def add_listing(body, message):
        listings.append((body['task'], body['args']))

    drain_queues(app, queue_names, callbacks=[add_listing], retain=True)
    return listings


def drain_queues(app, queue_names, callbacks=None, retain=False):
    """Drain the messages from queues.

    :param app: The app to list queues for (affects backend, Queue type,
        etc.).
    :param queue_names: Names of the queues to list.
    :param callbacks: Optional list of callbacks to call on each message.
        Callback must accept (body, message) as parameters.
    :param retain: After this operation, retain the messages in the queue.
    """
    if callbacks is None:
        callbacks = [lambda x, y: None]
    bindings = []
    router = app.amqp.Router()
    for queue_name in queue_names:
        destination = router.expand_destination(queue_name)
        exchange = Exchange(destination['exchange'])
        queue = Queue(queue_name, exchange=exchange)
        bindings.append(queue)
    with app.broker_connection() as connection:
        # The meaning of no_ack appears to be inverted.
        # See: https://github.com/ask/kombu/issues/126
        consumer = Consumer(
            connection, bindings, callbacks=callbacks, no_ack=not retain)
        with consumer:
            try:
                # Timeout of 0 causes error: [Errno 11] Resource temporarily
                # unavailable
                connection.drain_events(timeout=.1 ** 100)
            except timeout:
                pass
