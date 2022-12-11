import sys
from os.path import dirname, abspath

sys.path.append(dirname(dirname(abspath(__file__))) + "/src")
import src.parser as ps
import src.config as cf

import src
