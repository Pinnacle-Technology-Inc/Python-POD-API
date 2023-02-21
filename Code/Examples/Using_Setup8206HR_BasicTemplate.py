"""
Simple example template that runs Setup_8206HR. 
"""
# set path to <path>\Python-POD-API\Code\Modules
import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.path[0]),'Modules')) 

# local imports
from Setup_8206HR import Setup_8206HR

# authorship
__author__      = "Thresa Kelly"
__maintainer__  = "Thresa Kelly"
__credits__     = ["Thresa Kelly", "Seth Gabbert"]
__email__       = "sales@pinnaclet.com"
__date__        = "02/07/2023"

# ===============================================================

# setup 8206HR devices for streaming
go = Setup_8206HR()
go.Run()