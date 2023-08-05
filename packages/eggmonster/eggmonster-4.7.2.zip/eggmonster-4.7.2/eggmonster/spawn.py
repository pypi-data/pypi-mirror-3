def spawn_process(entry_point, args=(), **kwargs):
    if '.' in entry_point:
        raise ValueError, "Application entry point must not include package name: %s" % entry_point

    import os.path, sys
    exec_args = sys.argv[:]

    # Currently, only monster_run and emi are launching applications for Eggmonster,
    # and both support the --spawn flag.
    if os.path.basename(exec_args[0]) not in ('monster_run', 'emi'):
        raise RuntimeError("executable is not 'monster_run' or 'emi', it is %s" % exec_args[0])

    # First, remove any parameters we don't want to go to the spawned application.

    # If we have parameters intended for the target application, we can't
    # include those for the spawned application, so drop those parameters.
    try:
        delim_index = exec_args.index('!')
    except ValueError:
        pass
    else:
        del exec_args[delim_index:]

    # Also, if we have a spawned app invoking another spawned app, remove the
    # --spawn part of the command.
    for i, arg in enumerate(exec_args):
        if arg.startswith('--spawn='):
            del exec_args[i]
            break

    # Now to start adding parameters.
    exec_args[1:1] = ['--spawn=%s' % entry_point]

    # Add any command line parameters that have been requested.
    if args:
        exec_args.append('!')
        exec_args.extend([str(x) for x in args])

    import subprocess
    return subprocess.Popen(args=exec_args, **kwargs)
