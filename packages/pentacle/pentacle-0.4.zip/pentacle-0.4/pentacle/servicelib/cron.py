# A task-scheduling implementation.
# todo: a more unique name
from ..architecture import ServiceBase
from ..runtime import nth, Object

class CronManager(ServiceBase):
    NAME = 'System::Cron::Manager'

    class Task(Object):
        @classmethod
        def FromConfig(self, command, schedule):
            task = self(command)
            task.setSchedule(schedule)
            return task

        def __init__(self, command):
            self.command = command
        def setSchedule(self, scheduleString):
            pass
        def run(self):
            pass

    def Activate(self, apiMgr):
        ServiceBase.Activate(self, apiMgr)
        self.tasks = dict()

        # Load tasks from configuration.
        taskCommands = apiMgr.application.getConfigSection('Tasks').asDict()
        schedule = apiMgr.application.getConfigSection('Schedule')

        for option in schedule.options():
            try: cmd = taskCommands[option]
            except KeyError:
                continue

            self.tasks[option] = self.Task.FromConfig(cmd, schedule.getOption(option))

        def delaySchedule():
            # todo: calculate next delay from tasks.
            while True:
                yield ([], 10)

        waitForNextTask = delaySchedule().next

        # Start timing.
        def runScheduler():
            while True:
                (tasks, delay) = waitForNextTask()
                sleep(delay)

                for t in tasks:
                    # todo: post as apiMgr.application.engine message.
                    t.run()

        nth(runScheduler)
