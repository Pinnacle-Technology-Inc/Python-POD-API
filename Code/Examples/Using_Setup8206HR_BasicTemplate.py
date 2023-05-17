"""
Simple example template that runs Setup_8206HR. 
"""
# set path to <path>\Python-POD-API\Code\Modules
import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),'Modules')) 

# local imports
from Setup_8206HR_OLD import Setup_8206HR

# authorship
__author__      = "Thresa Kelly"
__maintainer__  = "Thresa Kelly"
__credits__     = ["Thresa Kelly", "Seth Gabbert"]
__license__     = "New BSD License"
__copyright__   = "Copyright (c) 2023, Thresa Kelly"
__email__       = "sales@pinnaclet.com"

# ===============================================================

# setup 8206HR devices for streaming
go = Setup_8206HR()
go.Run()
