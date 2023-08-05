import os
from nose import run

import sys
argv = list(sys.argv)

# since test modules in eggs frequently have exe bit set
argv.insert(1, "--exe")

run(
    # tell nose to look in passlib.tests dir
    defaultTest=os.path.dirname(__file__),
    
    # args
    argv = argv,
)

