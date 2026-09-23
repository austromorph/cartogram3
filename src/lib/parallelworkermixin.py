# -*- coding: utf-8 -*-


"""Provide a QgsTask-based drop-in replacement for
multiprocessing.imap_unordered()."""

import itertools

from qgis.core import (
    Qgis,
    QgsApplication,
    QgsMessageLog,
    QgsTask,
)

__all__ = ["ParallelWorkerMixin"]


TASK_DESCRIPTION = ""


class QgsDummyParentTask(QgsTask):  # pylint: disable=too-few-public-methods
    """QgsTask cannot be instantiated directly."""

    def run(self):
        return True


class ParallelWorkerMixin:
    """Provide a drop-in replacement for multiprocessing.imap_unordered()."""

    def __init__(self):
        """Initialise a QgsParallelWorker."""
        self.task = None
        self.results = []

    def cancel(self):
        """Cancel a running parallel task."""
        try:
            self.task.cancel()
        except AttributeError:
            pass

    def imap_unordered(self, func, iterable, /, chunksize=0):
        """Run `func` for every item in `iterable`"""
        task_manager = QgsApplication.taskManager()

        if chunksize > 0:
            chunks = itertools.batched(iterable, chunksize)
        else:
            chunks = [iterable]

        def _func(task, items):
            return_values = []
            for item in items:
                if task.isCanceled():
                    break
                return_values.append(func(item))
            return return_values

        self.task = task = QgsDummyParentTask(flags=QgsTask.CanCancel)
        for chunk in chunks:
            task.addSubTask(
                QgsTask.fromFunction(
                    TASK_DESCRIPTION,
                    _func,
                    chunk,
                    on_finished=self._finished,
                    flags=QgsTask.CanCancel,
                ),
                subTaskDependency=QgsTask.ParentDependsOnSubTask,
            )
        task_manager.addTask(task)

        task.waitForFinished(timeout=0)
        results = self.results

        self.task = None
        self.results = []

        return results

    def _finished(self, exception, result):
        if exception is not None:
            QgsMessageLog.logMessage(
                exception,
                level=Qgis.MessageLevel.Critical,
            )
            raise exception
        self.results.extend(result)
