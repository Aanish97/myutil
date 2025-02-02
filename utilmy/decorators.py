from threading import Thread
import cProfile, pstats, io
import os
import errno
import signal
from functools import wraps
import time
from contextlib import contextmanager


class _TimeoutError(Exception):
    """Time out error"""

    pass


def profile(fnc):

    """
    A decorator that uses cProfile to profile a function
    And print the result
    """

    def inner(*args, **kwargs):

        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = "cumulative"
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner


def threading_d(func):

    """
    A decorator to run function in background on thread

	Args:
		func:``function``
			Function with args

	Return:
		background_thread: ``Thread``

    """

    @wraps(func)
    def wrapper(*args, **kwags):
        background_thread = Thread(target=func, args=(*args,))
        background_thread.daemon = True
        background_thread.start()
        return background_thread

    return wrapper


def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    """
    Decorator to throw timeout error, if function doesnt complete in certain time

    Args:
        seconds:``int``
            No of seconds to wait
        error_message:``str``
            Error message

    """

    def decorator(func):
        def _handle_timeout(signum, frame):
            raise _TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


def timer(func):
    """
    Decorator to show the execution time of a function or a method in a class.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f'function {func.__name__} finished in: {(end - start):.2f} s')
        return result

    return wrapper


@contextmanager
def context_profiler():
    """
    Context Manager the will profile code inside it's bloc.
    And print the result of profiler.
    Example:
        with context_profiler():
            # code to profile here

    """
    from pyinstrument import Profiler
    profiler = Profiler()
    profiler.start()
    try:
        yield profiler
    except Exception as e:
        raise e
    finally:
        profiler.stop()
        print(profiler.output_text(unicode=True, color=True))


def profiled(func):
    """
    A decorator that will profile a function
    And print the result of profiler.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from pyinstrument import Profiler
        profiler = Profiler()
        profiler.start()
        result = func(*args, **kwargs)
        profiler.stop()
        print(profiler.output_text(unicode=True, color=True))
        return result
    return wrapper


def os_multithread(**kwargs):
    """
    Creating n number of threads, starting them
    and waiting for their subsequent completion

    Parameters
    ----------
    kwargs: list of dictionaries, where each key-value pair is the
    usage name and tuple of function name and function arguments,
    Example:
        os_multithread(function1=(function_name1, (arg1, arg2, ...)),
                       function2=(function_name2, (arg1,)),
                       function3=(function_name3, (,)),
                       ...)

    Returns list of return values from the functions passed
    -------

    """

    class ThreadWithResult(Thread):
        def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, *, daemon=None):
            def function():
                self.result = target(*args, **kwargs)

            super().__init__(group=group, target=function, name=name, daemon=daemon)

    list_of_threads = []
    for thread in kwargs.values():
        t = ThreadWithResult(target=thread[0], args=thread[1])
        list_of_threads.append(t)

    for thread in list_of_threads:
        thread.start()

    results = []
    for thread, keys in zip(list_of_threads, kwargs.keys()):
        thread.join()
        results.append((keys, thread.result))

    return results
