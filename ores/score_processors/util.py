import signal


def timeout_handler(signum, frame):
    raise RuntimeError("Function execution timed out.")

def timeout(func, seconds=None):
    if seconds is not None:
        result = func()
    else:
        # Set the signal handler and a 5-second alarm
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(seconds)

        # This func() may hang indefinitely
        result = func()

        signal.alarm(0)          # Disable the alarm

    return result
