from django_cron import CronJobBase, Schedule
from notifications import check_for_updates_and_notify

class UpdateCheckCron(CronJobBase):

    schedule = Schedule(run_every_mins=60)
    code = 'AdminCP.update_check_cron'

    def do(self):
        check_for_updates_and_notify()