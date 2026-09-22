# -*- coding: utf-8 -*-


"""Provide a drop-in replacement for multiprocessing.imap_unordered() using QgsTasks."""

import itertools

from qgis.core import (
    QgsApplication,
    QgsTask,
)

TASK_DESCRIPTION = ""


class QgsDummyParentTask(QgsTask):  # pylint: disable=too-few-public-methods
    """QgsTask cannot be instantiated directly."""


class QgsParallelWorker:
    """Provide a drop-in replacement for multiprocessing.imap_unordered()."""

    def __init__(self):
        """Initialise a QgsParallelWorker."""
        self.task = None

    def cancel(self):
        """Cancel a running parallel task."""
        try:
            self.task.cancel()
        except AttributeError:
            pass

    def imap_unordered(self, func, iterable, /, chunksize=1):
        """Run `func` for every item in `iterable`"""
        task_manager = QgsApplication.taskManager()

        if chunksize > 1:
            chunks = itertools.batched(iterable, chunksize)
        else:
            chunks = [iterable]

        results = []

        def _func(task, items):
            return_values = []
            for item in items:
                if task.isCancelled():
                    break
                return_values.append(func(item))
            return return_values

        def _finished(exception, result):
            if exception is not None:
                print(exception)
                raise exception
            results.extend(result)

        self.task = task = QgsDummyParentTask(flags=QgsTask.CanCancel)
        for chunk in chunks:
            task.addSubTask(
                QgsTask.fromFunction(
                    TASK_DESCRIPTION,
                    _func,
                    chunk,
                    on_finished=_finished,
                    flags=QgsTask.CanCancel,
                ),
                subTaskDependency=QgsTask.ParentDependsOnSubTask,
            )
        task_manager.addTask(task)

        task.waitForFinished(timeout=0)
        self.task = None

        return results
