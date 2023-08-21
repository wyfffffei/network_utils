#!/usr/local/bin/python3

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)).split(os.sep)[:-2]
sys.path.append(os.sep.join(SCRIPT_DIR))

from network_utils.tools import dict2json

from network_utils.conf_parser import FortiGate
FT = FortiGate("cfgbackup_ft_fw01.conf")
dict2json(FT.parse_policy(), "ft_output.json")

from network_utils.conf_parser import CheckPoint
CP = CheckPoint("gaia_os_cp_gw.txt")
dict2json(CP.parse_configuration(), "cp_output.json")


