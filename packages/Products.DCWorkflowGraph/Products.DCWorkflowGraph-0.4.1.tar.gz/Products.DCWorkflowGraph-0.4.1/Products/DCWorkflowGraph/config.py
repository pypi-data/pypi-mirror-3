# where is 'pot'?, add your path here

import os

DOT_EXE = 'dot'
bin_search_path = ''

if os.name == 'nt':
    DOT_EXE = 'dot.exe'

    # patch from Joachim Bauch bauch@struktur.de
    # on Windows, the path to the ATT Graphviz installation 
    # is read from the registry. 
    try:
        import win32api, win32con
        # make sure that "key" is defined in our except block
        key = None
        try:
            key = win32api.RegOpenKeyEx(win32con.HKEY_LOCAL_MACHINE, r'SOFTWARE\ATT\Graphviz')
            value, type = win32api.RegQueryValueEx(key, 'InstallPath')
            bin_search_path = [os.path.join(str(value), 'bin')]
        except:
            if key: win32api.RegCloseKey(key)
            # key doesn't exist
            pass
    except ImportError:
        # win32 may be not installed...
        pass
else:
    # for posix systems
    DOT_EXE = 'dot'
    path = os.getenv("PATH")
    bin_search_path = path.split(":")

