from pprint import pprint
import sys

# sys.path is a list of absolute path strings
from os.path import dirname, abspath

pprint(sys.path)
d = dirname(dirname(abspath(__file__)))

sys.path.append(d)
pprint(sys.path)

import src
