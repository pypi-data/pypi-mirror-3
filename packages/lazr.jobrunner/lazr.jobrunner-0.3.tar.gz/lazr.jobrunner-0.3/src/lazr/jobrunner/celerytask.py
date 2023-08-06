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


from celery.task import Task
from functools import partial
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
