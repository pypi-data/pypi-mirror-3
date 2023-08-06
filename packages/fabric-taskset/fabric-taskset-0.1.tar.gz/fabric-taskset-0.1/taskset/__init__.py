# -*- coding: utf-8 -*-
from __future__ import absolute_import
import inspect
import sys
from fabric.tasks import WrappedCallableTask

def task(*args, **kwargs):
    """
    Decorator declaring the wrapped method to be task.

    It acceps the same arguments as ``fabric.decorators.task`` so
    use it on methods just like fabric's decorator is used on functions.

    The class decorated method belongs to should be a subclass
    of :class:`.TaskSet`.
    """

    invoked = bool(not args or kwargs)
    if not invoked:
        func, args = args[0], ()

    def decorator(func):
        func._task_info = dict(
            args = args,
            kwargs = kwargs
        )
        return func

    return decorator if invoked else decorator(func)



class TaskSet(object):
    """
    TaskSet is a class that can expose its methods as Fabric tasks.

    Example::

        # my_lib/say.py
        from taskset import TaskSet, task

        class SayBase(TaskSet):
            def say(self, what):
                raise NotImplemented()

            @task(default=True, alias='hi')
            def hello(self):
                self.say('hello')

        class EchoSay(SayBase):
            def say(self, what):
                local('echo ' + what)

        instance = EchoSay()
        instance.expose_to_current_module()

        # fabfile.py
        from mylib import say

    and then::

        $ fab say.hi
    """

    def expose_to(self, module_name):
        """
        Adds tasks to module which name is passed in ``module_name`` argument.
        Returns a list of added tasks names.

        Example::

            instance = MyTaskSet()
            __all__ = instance.expose_to(__name__)
        """
        return list(self._expose_to(module_name))

    def expose_to_current_module(self):
        """
        The same as :meth:`TaskSet.expose_to` but magically
        addds tasks to current module.

        Example::

            instance = MyTaskSet()
            __all__ = instance.expose_to_current_module()
        """
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        return self.expose_to(mod.__name__)

    def _expose_to(self, module_name):
        module_obj = sys.modules[module_name]
        for name, task in self._get_fabric_tasks():
            setattr(module_obj, name, task)
            yield name

    def _is_task(self, func):
        return hasattr(func, '_task_info')

    def _task_for_method(self, method):
        return WrappedCallableTask(method, *method._task_info['args'], **method._task_info['kwargs'])

    def _get_fabric_tasks(self):
        return (
            (name, self._task_for_method(task))
            for name, task in inspect.getmembers(self, self._is_task)
        )
