"""A simple stack-based performance logger.

Wallclock provides some simple tools for identifying slow parts of your code.
It maintains a stack of running timers, and reports the tree of execution
times when the stack empties out.

Simple Usage
------------

To time code with wallclock, use the ``push`` and ``pop`` functions provided
by the wallclock module::

    import wallclock
    
    def slow_function():
        wallclock.push('slow function')
        import time
        time.sleep(3)
        wallclock.pop('slow function')
    
    def main():
        wallclock.push('handling one request', enable=True)
        slow_function()
        wallclock.pop('handling one request')
    
    main()

This will produce a small tree on ``stderr`` summarizing the time taken to
execute ``main()``::

    [3.001 sec] handling one request
      [3.001 sec] slow function

The ``push`` function takes one positional argument, which is the label of the
timer being pushed onto wallclock's stack. This is normally a short,
descriptive label for the kind of work that happens under timing. ``push``
also takes one optional keyword argument, ``enable``, which controls whether
this call to ``push`` should start timing (if it's not already started).
``wallclock`` ignores calls to ``push`` until it has been enabled, and
disables itself automatically when the enabling ``push`` is ``pop``ped.

The ``pop`` function takes one positional argument, which is the label to pop.
This allows for simple insertion of ``push``/``pop`` pairs surrounding code
that might return, or might raise an exception, without adding extra
``try``/``except`` blocks or similar (but see below for a better approach).
``wallclock`` will pop timers off of the stack until it finds a timer pushed
with the passed label, or until it empties the timer stack.

Configuration
-------------

``wallclock`` exposes two module-scoped symbols that can be used to control
its behaviour:

* ``wallclock.threshold`` is a number (``float``, ``int``, or ``long``) of
  seconds. Any timers whose duration is strictly less than ``threshold`` will
  not be recorded. By default, the threshold is approximately 10 milliseconds
  (0.01 seconds). Setting the threshold to ``0`` will record every timer.
* ``wallclock.output`` is a callable object used to print recorded times. By
  default, it's set to ``wallclock.stderr_output``, which writes the tree to
  standard error, but applications can replace this with their own callables.
  ``wallclock`` invokes ``output`` with one  argument, which is the root timer
  object. Timer objects have three readable properties:
  1. ``label``, which is the label passed to ``push`` when the timer was
     created.
  2. ``duration``, which is the total time recorded on the timer (in seconds).
  3. ``children``, which is a sequence of timer objects that were recorded
     while the passed timer object was at the top of the stack.

Automatic Timer Management
--------------------------

Manually inserting calls to ``push`` and ``pop`` works for debugging, but not
so well for leaving wallclock in place afterwards. The ``wallclock`` module
provides some tidier alternatives.

Context Manager
~~~~~~~~~~~~~~~

The ``wallclock.block`` context manager automatically calls ``push`` before
evaluating the block, and ensures ``pop`` is called after exiting the block by
any means::

    import wallclock
    
    def slow_function():
        with wallclock.block('slow function'):
            import time
            time.sleep(3)
    
    def main():
        with wallclock.block('handling one request', enable=True):
            slow_function()
    
    main()

The ``block`` context manager accepts the same arguments that ``push``
accepts: a positional argument labelling the block, and an optional keyword
argument called ``enable`` for controlling whether the block should start
wallclock (if it's not already started).

Decorators
~~~~~~~~~~

The ``wallclock.function`` and ``wallclock.trace_function`` decorators
automatically call ``push`` before executing the decorated function, and
automatically call ``pop`` after the function exits, but before returning to
the caller::

    import wallclock
    
    @wallclock.function
    def slow_function():
        import time
        time.sleep(3)
    
    @wallclock.trace_function
    def main():
        slow_function()
    
    main()

Both decorators determine the label for the pushed timer by examining the
called function's module and name. ``trace_function`` enables wallclock, while
``function`` does not.

Threads
-------

Wallclock makes a reasonable effort to keep a timer stack for each thread.
Timer stacks are kept in a ``threading.threadlocal`` object and are enabled
and disabled on a per-thread basis.

Performance
-----------

Timing your code is not free. While wallclock is noticably faster than a full
profiler, it still introduces overhead to manage the stack of pending timers
and the tree of completed timers. I've found the overhead to be surprisingly
large (a decorated empty function takes ~100x as long as a naked empty
function), but still well within usable limits.

Removing calls that enable wallclock reduces this overhead considerably. You
can further reduce overhead by disabling ``wallclock`` completely by calling
``wallclock.smash()``. This is an irreversible operation which replaces the
``push`` and ``pop`` operations, the ``block`` context manager, and the
``function`` and ``trace_function`` decorators with no-op equivalents.
"""

import datetime as dt
import sys
import contextlib as c
import decorator as d
import threading as t

def stderr_output(observation, _depth=0):
    """A wallclock output function that dumps timing as a textual tree on
    standard error.
    
    This function is configured as ``wallclock.output`` by default. To restore
    this function after configuring a different output function, assign it to
    ``wallclock.output``.
    """
    indent = _depth * "  "
    print >>sys.stderr, "%s[%#.3f sec] %s" % (
        indent,
        observation.duration,
        observation.label
    )
    for child in observation.children:
        stderr_output(child, _depth=_depth + 1)

class ObservedDuration(object):
    """A tree (or subtree) of labelled timing observations. Wallclock creates
    and maintains these as callers push and pop timers, building up a tree
    of completed observations. ``ObservedDuration`` objects should be created
    using the ``start`` class method, which takes (as a positional argument)
    a label for the newly-created observation and records the time at which
    the observation was started.
    
    Each ``ObservedDuration`` has three readable properties:
    
    * ``label``, the label passed when the observation was pushed.
    * ``duration``, the number of seconds (as a ``float``) within the
      observation. This is ``None`` until the observation is ``mark()``ed.
    * ``children``, a sequence of observations recorded while this observation
      was at the top of the stack.
    
    Additionally, ``ObservedDuration`` objects support the following methods:
    
    * ``mark()``, which records the current time into the observation's mark.
      The observation's ``duration`` property is set to the difference, in
      seconds, between the time at which the observation was started and the
      time at which it was marked.
    * ``add_child(observation)``, which records an observation (as an
      ``ObservedDuration`` object, or anything compatible with its interface)
      at the end of the observation's ``children`` sequence.
    """
    @classmethod
    def start(cls, label):
        """Creates a new observation, recording the creation time. This method
        takes a single positional parameter, which labels the created
        observation.
        
        The created observation is initially un-marked, and has a ``duration``
        of ``None``. It initially has no ``children``.
        """
        return cls(label, dt.datetime.now())
    
    def __init__(self, label, start):
        self.label = label
        self.started_at = start
        self.marked_at = None
        self.children = []
    
    def mark(self):
        """Marks the observation, recording the marking time. The ``duration``
        is the difference, in seconds, from the observation's creation time to
        the observation's marking time.
        """
        self.marked_at = dt.datetime.now()
        return self.marked_at - self.started_at
    
    @property
    def duration(self):
        if self.marked_at is None:
            return None
        return (self.marked_at - self.started_at).total_seconds()
    
    def add_child(self, observation):
        """Records an observation at the end of this observation's
        ``children``.
        """
        self.children.append(observation)
    
    def __str__(self):
        return "Observed duration for %s: started %s, marked %s, %s %s" % (
            self.label,
            self.started_at,
            self.marked_at if self.marked_at is not None else 'never',
            len(self.children),
            'child' if len(self.children) == 1 else 'children'
        )

_thread_data = t.local()
_thread_data.timer_stack = None

output = stderr_output
threshold = 0.01

def push(label, enable=False):
    """Push a timer onto the timer stack.
    
    A new timer with the passed label will be pushed onto the timer stack, if
    an enabled push is still on the stack. The timer can be popped back off
    the stack by calling ``pop`` with the same label, which records the
    time period for which the timer was on the stack.
    
    This function takes a positional parameter, which labels the pushed timer,
    and an optional keyword parameter, ``enable``, which controls whether this
    push should turn timer recording on if not already running.
    """
    if _thread_data.timer_stack is None:
        if enable:
            _thread_data.timer_stack = []
        else:
            return
    observation = ObservedDuration.start(label)
    _thread_data.timer_stack.append(observation)

def _pop():
    observation = _thread_data.timer_stack.pop()
    duration = observation.mark()
    if len(_thread_data.timer_stack) > 0:
        if duration.total_seconds() >= threshold:
            _thread_data.timer_stack[-1].add_child(observation)
    else:
        _thread_data.timer_stack = None
    return observation

def pop(label):
    """Pops the named timer off the timer stack.
    
    This pops timers off the stack until the named timer is found and popped,
    recording the durations of the popped timers as it goes. If it pops off
    the bottom-most call to ``push`` that enabled timing, this passes the
    gathered timing to the ``wallclock.output`` callable for output and
    disables timer recording.
    
    If timer recording is not enabled, this function does nothing.
    """
    if _thread_data.timer_stack is None:
        return
    observation = _pop()
    while label != observation.label:
        observation = _pop()
    if _thread_data.timer_stack is None:
        output(observation)

@c.contextmanager
def block(label, enable=False):
    """Wraps the evaluation of a block with a ``push``/``pop`` pair.
    
    This accepts the same arguments as ``push``: a positional label parameter,
    and optionally an ``enable`` keyword argument controlling whether the push
    should activate timing if not already active.
    """
    push(label, enable)
    try:
        yield
    finally:
        pop(label)

@d.decorator
def function(f, *args, **kwargs):
    """Wraps the evaluation of a functino with a ``push``/``pop`` pair. The
    timer's label will be derived from the function's module and name, and
    timing will not be enabled if not already active.
    
    To activate timing automatically when calling a function, use the
    ``trace_function`` decorator instead.
    """
    label = '%s.%s' % (f.__module__, f.__name__)
    with block(label):
        return f(*args, **kwargs)

@d.decorator
def trace_function(f, *args, **kwargs):
    """Wraps the evaluation of a functino with a ``push``/``pop`` pair. The
    timer's label will be derived from the function's module and name, and
    timing will be enabled if not already active.
    
    To record timing without automatically enabling wallclock, use the
    ``function`` decorator instead.
    """
    label = '%s.%s' % (f.__module__, f.__name__)
    with block(label, enable=True):
        return f(*args, **kwargs)

def smash():
    """Disable Wallclock.
    
    This is an irreversible operation. ``smash`` replaces the ``push`` and
    ``pop`` functions, the ``block`` context manager, and the ``function``
    and ``trace_function`` decorators, along with several internal functions,
    with no-ops. This reduces wallclock's overhead to an absolute minimum
    without making modifications to your code.
    """
    global push
    def push(label, enable=False):
        pass
    
    global pop
    def pop(label):
        pass
    
    global _pop
    def _pop(label):
        pass
    
    global block
    @c.contextmanager
    def block(label, enable=False):
        yield
    
    global function
    def function(f):
        return f
    
    global trace_function
    def trace_function(f):
        return f
