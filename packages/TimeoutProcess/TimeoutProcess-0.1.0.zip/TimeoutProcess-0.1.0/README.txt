==============
TimeoutProcess
==============

TimeoutProcess provides the ability to run a process with a specified time out.
You may find it useful when trying to run a process, which may not terminate
in a reasonably obvious fashion. Obvious examples would be typical GUI applications
which run till they are explicitly closed.

Typical usage of TimeoutProcess looks like this::

    #!/usr/bin/env python

    import timeoutprocess

    timeoutprocess.TimeoutProcess(['notepad.exe', r'c:\\myfile.txt'], 60)

The first argument to TimeoutProcess take the form of the arguments to
subprocess.Popen(), which is a list containing the program name, and any
additional arguments.

The second argument is the time, in seconds, to allow the process to run.

