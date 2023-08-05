#
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
import pickle
from apscheduler.scheduler import Scheduler as APScheduler
from coils.core import BLOBManager

JOB_UUID      = 0
JOB_ROUTEID   = 1
JOB_CONTEXTID = 2
JOB_INPUT     = 3

SCHED_ROUTEID   = 0
SCHED_CONTEXTID = 1
SCHED_INPUT     = 2
SCHED_TRIGGER   = 3
SCHED_PARAMS    = 4

class CronThread(APScheduler):

    def __init__(self, service, **config):
        self._service = service
        APScheduler.__init__(self, **config)
        self._crontab = { }
        self.load_schedule()

    @property
    def log(self):
        return self._service.log

    #
    # Preserve state
    #

    def save_schedule(self):
        # TODO: Implement
        self.jobs_lock.acquire()
        try:
            # Rebuild crontab filtering out expired jobs
            tab = {}
            uuids = [job.args[JOB_UUID] for job in self.jobs]
            for key in self._crontab:
                if key in uuids:
                    tab[key] = self._crontab[key]
            self._crontab = tab
            # Save crontab
            source = BLOBManager.Create('.crontab', encoding='binary')
            pickle.dump(self._crontab, source)
            BLOBManager.Close(source)
        except Exception, e:
            raise e
        finally:
            self.jobs_lock.release()

    def load_schedule(self):
        try:
            source = BLOBManager.Open('.crontab', 'rb', encoding='binary')
            if (source is not None):
                x = pickle.load(source)
                self.log.error(x)
                self._crontab = x
                BLOBManager.Close(source)
                for uuid in self._crontab:
                    value = self._crontab[uuid]
                    self.log.debug('processing crontab entry {0} type {1}'.format(uuid, value[3]))
                    if (value[SCHED_TRIGGER] == 'date'):
                        self.add_date_job(self._service._queue_process,
                                          value[SCHED_PARAMS][0],
                                          args=(key, value[SCHED_ROUTEID], value[SCHED_CONTEXTID], value[SCHED_INPUT]))
                    elif (value[SCHED_TRIGGER] == 'interval'):
                        self.add_interval_job(self._service._queue_process,
                                              weeks      = value[SCHED_PARAMS][0],
                                              days       = value[SCHED_PARAMS][1],
                                              hours      = value[SCHED_PARAMS][2],
                                              minutes    = value[SCHED_PARAMS][3],
                                              seconds    = value[SCHED_PARAMS][4],
                                              start_date = value[SCHED_PARAMS][5],
                                              repeat     = value[SCHED_PARAMS][6],
                                              args       = (uuid, value[SCHED_ROUTEID], value[SCHED_CONTEXTID], value[SCHED_INPUT]))
                    elif (value[SCHED_TRIGGER] == 'crontab'):
                        self.log.debug('restoring chronological job; year={0} month={1} day={2} dow={3} hour={4} minute={5}'.\
                            format(value[SCHED_PARAMS][0], value[SCHED_PARAMS][1], value[SCHED_PARAMS][2],
                                   value[SCHED_PARAMS][3], value[SCHED_PARAMS][4], value[SCHED_PARAMS][5]))
                        self.add_cron_job(self._service._queue_process,
                                          year        = value[SCHED_PARAMS][0],
                                          month       = value[SCHED_PARAMS][1],
                                          day         = value[SCHED_PARAMS][2],
                                          day_of_week = value[SCHED_PARAMS][3],
                                          hour        = value[SCHED_PARAMS][4],
                                          minute      = value[SCHED_PARAMS][5],
                                          args        = (uuid, value[SCHED_ROUTEID], value[SCHED_CONTEXTID], value[SCHED_INPUT]))
                        self.log.debug('job {0} restored to schedule'.format(uuid))
        except Exception, e:
            self.log.error('Error loading crontab from persistent store.')
        finally:
            self.log.info('{0} entries loaded from persisted schedule of processes'.format(len(self._crontab)))

    #
    # Add-job overloads
    #

    def add_date_job(self, func, date, args=None):
        APScheduler.add_date_job(self, func, date, args=args)
        self._crontab[args[JOB_UUID]] = (args[JOB_ROUTEID], args[JOB_CONTEXTID], args[JOB_INPUT],
                                         'date', (date))
        self.save_schedule()

    def add_interval_job(self, func, weeks=0, days=0, hours=0, minutes=0,
                                     seconds=0, start_date=None, repeat=0,
                                     args=None):
        APScheduler.add_interval_job(self, func, weeks=weeks, days=days, hours=hours, minutes=minutes,
                                                 seconds=seconds, start_date=start_date, repeat=repeat,
                                                 args=args)
        self._crontab[args[JOB_UUID]] = (args[JOB_ROUTEID], args[JOB_CONTEXTID], args[JOB_INPUT],
                                        'interval', (weeks, days, hours, minutes, seconds, start_date, repeat))
        self.save_schedule()


    def add_cron_job(self, func, year='*', month='*', day='*', day_of_week='*',
                     hour='*', minute='*', args=None):
        APScheduler.add_cron_job(self, func, year=year, month=month, day=day, day_of_week=day_of_week,
                                             hour=hour, minute=minute, second='0', args=args)
        self._crontab[args[JOB_UUID]] = (args[JOB_ROUTEID], args[JOB_CONTEXTID], args[JOB_INPUT],
                                         'crontab', (year, month, day, day_of_week, hour, minute))
        self.save_schedule()


    #
    # Cancel jobs
    #

    def _unschedule_jobs(self, key, value, contexts):
        self.log.info('Request to cancel job UUID:{0}'.format(value))
        self.jobs_lock.acquire()
        result = False
        try:
            if (10000 in contexts) or (10100 in contexts):
                jobs = [job for job in self.jobs if ((job.args[key] == value))]
            else:
                jobs = [job for job in self.jobs if ((job.args[key] == value) and (job.args[JOB_CONTEXTID] in contexts))]
            self.log.info('Found {0} jobs for cancellation request'.format(len(jobs)))
            if (len(jobs) > 0):
                for job in jobs:
                    self.jobs.remove(job)
                    del self._crontab[job.args[JOB_UUID]]
                    result = True
        finally:
            self.jobs_lock.release()
        self.wakeup.set()
        self.save_schedule()
        return result

    def cancel_job_by_uuid(self, uuid, contexts):
        return self._unschedule_jobs(JOB_UUID, uuid, contexts)

    def cancel_jobs_for_route(self, route_id):
        return self._unschedule_job(JOB_ROUTEID, uuid, contexts)

    def cancel_jobs_for_context(self, context_id):
        return self._unschedule_job(JOB_CONTEXTID, uuid, contexts)

    #
    # Report jobs
    #

    def list_jobs(self, key=None, value=None):
        result = []
        self.jobs_lock.acquire()
        try:
            if (key is None):
                uuids = [job.args[JOB_UUID] for job in self.jobs]
            else:
                uuids = [job.args[JOB_UUID] for job in self.jobs if job.args[key] == value]
            for uuid in uuids:
                entry = self._crontab.get(uuid)
                result.append((uuid, entry[SCHED_ROUTEID], entry[SCHED_CONTEXTID], entry[SCHED_INPUT],
                                     entry[SCHED_TRIGGER], entry[SCHED_PARAMS]))
        finally:
            self.jobs_lock.release()
        return result

    def list_all_jobs_for_context(self, ctx_id):
        return self.list_jobs(key=JOB_CONTEXTID, value=ctx_id)

    def list_all_jobs_for_route(self, route_id):
        return self.list_jobs(key=JOB_ROUTEID, value=route_id)
