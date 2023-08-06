import subprocess
import threading

class TimeoutProcess(threading.Thread):
  '''
  Run a process, with a timeout.

  This class derives from threading.Thread, and uses threads
  to start a new process. The arguments to the class are
  a command line (in subprocess.Popen() format), as well as
  a time out in seconds. The process specified in the command
  line is then run, for a maximum of the time specified in
  time out.

  '''

  def __init__(self, cmd, timeout):
    '''
    Constructor.

    Creates a threading object that can be started, and
    populate the necessary cmd field (required for threading).
    Also store the time out that the user specified.

    Starts the process in a separate thread, and then block
    the main thread (this thread) for the specific amount of
    time specified in the time out. That leaves the process
    to execute freely for that amount of time. Once that time
    has elapsed, unblock the main thread and kill the process,
    if it's still alive.

    '''
    # Store command line and time out value.
    threading.Thread.__init__(self)
    self.cmd = cmd
    self.timeout = timeout

    # Start the process
    self.start()

    # Block ourselves until time out reached.
    # Once time is up, unblock ourselves, and take action.
    self.join(self.timeout)

    # Check if the thread still alive.
    # If it's dead, nothing to do, else kill it.
    if self.is_alive():
      self.p.terminate()
      self.join()

  def run(self):
    '''
    Thread's run method.

    This method specifies what to do when this thread is to
    be 'started'. In this case, we simply use subprocess.Popen()
    to spawn the process. Hence, a new thread (this thread) is
    used to create a new process.

    '''
    self.p = subprocess.Popen(self.cmd)
    self.p.wait()

