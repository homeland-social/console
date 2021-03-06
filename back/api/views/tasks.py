import logging
from datetime import datetime, timedelta

from flask import request
from flask_peewee.utils import get_object_or_404
from restless.preparers import FieldsPreparer

from api.models import Task, TaskLog
from api.views import BaseResource
from api.tasks import cron


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


@cron('0 0 * * *')
def purge_tasks():
    "Delete tasks that created more than 30 days ago."
    tasks = Task \
        .select() \
        .where(Task.created <= datetime.now() - timedelta(days=30))
    for task in tasks:
        yield f'Deleting task: {task.id}, created={task.create}'
        task.delete_instance()


class ResultPreparer(FieldsPreparer):
    "Handle special cases."

    def lookup_data(self, lookup, data):
        "function and result fields are callables that we don't want called."
        if lookup == 'function':
            return data.function.__name__
        elif lookup == 'result':
            try:
                return data.get_result()
            except Exception as e:
                return exc_preparer.prepare({
                    'type': 'Exception',
                    'value': str(e),
                })
        return super().lookup_data(lookup, data)


exc_preparer = FieldsPreparer(fields={
    'type': 'type',
    'value': 'value',
})

task_preparer = ResultPreparer(fields={
    'id': 'id',
    'function': 'function',
    'result': 'result',
    'created': 'created',
    'completed': 'completed',
    'tail': 'tail.message',
})


class TaskResource(BaseResource):
    "Manage settings."
    preparer = task_preparer
    extra_actions = {
        'cancel': ['POST'],
    }

    def list(self):
        "List all tasks."
        status = request.args.get('status')
        function = request.args.get('function')
        tasks = Task.select().join(TaskLog)
        if status == 'active':
            tasks = tasks.where(Task.completed.is_null(True))
        elif status == 'complete':
            tasks = tasks.where(Task.completed.is_null(False))
        if function:
            tasks = tasks.where(Task.function == function)
        return tasks

    def detail(self, pk):
        "Retrieve single task."
        return get_object_or_404(Task, Task.id == pk)

    def delete(self, pk):
        "Delete task."
        task = get_object_or_404(Task, Task.id == pk)
        task.delete_instance()

    def delete_list(self):
        Task.delete().execute()

    def cancel(self, pk):
        "Cancel task."
        task = get_object_or_404(Task, Task.id == pk)
        task.cancel()
        return task


class TaskLogResource(BaseResource):
    "Log output for a task."
    preparer = FieldsPreparer(fields={
        'created': 'created',
        'message': 'message',
    })

    def list(self, task_pk):
        task = get_object_or_404(Task, Task.id == task_pk)
        return TaskLog \
            .select() \
            .where(TaskLog.task == task) \
            .order_by(Task.created.desc())

    def detail(self, task_pk, pk):
        return get_object_or_404(
            TaskLog, TaskLog.task_id == task_pk, TaskLog.id == pk)
