#!/usr/bin/python
#dhn.py
#
#    Copyright DataHaven.NET LTD. of Anguilla, 2006-2011
#    All rights reserved.
#

import os
import sys


##if __name__ == "__main__":
##    from p2p.dhnmain import main
##    dirpath = os.path.dirname(os.path.abspath(sys.argv[0]))
##    os.chdir(os.path.join(dirpath, 'p2p'))
##    sys.argv[0] = 'dhnmain.py'
##    main()

if __name__ == "__main__":
    #executable_dir_path = os.path.abspath(os.path.dirname(os.path.abspath(sys.argv[0])))
    #if os.path.abspath(os.getcwd()) != executable_dir_path:
        #os.chdir(executable_dir_path)
    import p2p.dhnmain
    ret = p2p.dhnmain.main()
    if ret == 2:
        print p2p.dhnmain.usage()
    sys.exit(ret)
