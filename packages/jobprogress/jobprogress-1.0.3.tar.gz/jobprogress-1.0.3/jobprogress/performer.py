# Created By: Virgil Dupras
# Created On: 2010-11-19
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from threading import Thread
import sys

from .job import Job, JobInProgressError, JobCancelled

class ThreadedJobPerformer:
    """Run threaded jobs and track progress.
    
    To run a threaded job, first create a job with _create_job(), then call _run_threaded(), with 
    your work function as a parameter.
        
    Example:
        
    j = self._create_job()
    self._run_threaded(self.some_work_func, (arg1, arg2, j))
    """
    _job_running = False
    _last_error = None
    
    #--- Protected
    def create_job(self):
        if self._job_running:
            raise JobInProgressError()
        self.last_progress = -1
        self.last_desc = ''
        self.job_cancelled = False
        return Job(1, self._update_progress)
    
    def _async_run(self, *args):
        target = args[0]
        args = tuple(args[1:])
        self._job_running = True
        self._last_error = None
        try:
            target(*args)
        except JobCancelled:
            pass
        except Exception:
            self._last_error = sys.exc_info()
        finally:
            self._job_running = False
            self.last_progress = None
    
    def _reraise_if_error(self):
        """Reraises the error that happened in the thread if any.
        
        Call this after the caller of run_threaded detected that self._job_running returned to False
        """
        if self._last_error is not None:
            _, value, tb = self._last_error
            raise value.with_traceback(tb)
    
    def _update_progress(self, newprogress, newdesc=''):
        self.last_progress = newprogress
        if newdesc:
            self.last_desc = newdesc
        return not self.job_cancelled
    
    def run_threaded(self, target, args=()):
        if self._job_running:
            raise JobInProgressError()
        args = (target, ) + args
        Thread(target=self._async_run, args=args).start()
    
