# local imports
from PodApi.Parameters import Params8229

# authorship
__author__      = "Thresa Kelly"
__maintainer__  = "Thresa Kelly"
__credits__     = ["Thresa Kelly", "Sree Kondi", "Seth Gabbert"]
__license__     = "New BSD License"
__copyright__   = "Copyright (c) 2023, Thresa Kelly"
__email__       = "sales@pinnaclet.com"


def RunTests(printTests: bool = True) -> tuple[int,int]: 
    """Run all tests on Params8229

    Args:
        printTests (bool, optional): Make True to print the test results and messages. Defaults to True.
    
    Returns:
        tuple[int,int]: First item is the number of passed tests. Last item is the total number of tests
    """
    # collect all tests
    tests = {
        "1. Empty Schedule:\t"      : Test1_EmptySched,
        "2. Match Init:\t\t"        : Test2_MatchInit,
        "3. Check System ID:\t"     : Test3_BadSystemID,
        "4. Check Motor Speed:\t"   : Test4_BadMotorSpeed,
        "5. Check Mode:\t\t"        : Test5_BadMode,
        "6. Check Base Time:\t"     : Test6_BadReverseBaseTime,
        "7. Check Var Time:\t"      : Test7_BadReverseVarTime,
        "8. Check Schedule:\t"      : Test8_BadSchedule,
    }
    # run all 
    tests: dict[str,tuple[bool,str]] = {key : _ErrorWrap(val) for (key,val) in tests.items()}
    # get total status 
    passed = sum([int(x[0]) for x in tests.values()])
    total = len(tests.keys())
    # show results 
    if(printTests) : 
        print("== Testing: Params8229 ==")
        [print(key, val[0], val[1]) for (key,val) in tests.items()]
        print("Passed "+str(passed)+" of "+str(total))
    return (passed, total)  

def _ErrorWrap(function) : 
    try : 
        return (function())
    except Exception as e :
        return (False, ' - Unexpected Exception: '+str(e))
    

def Test1_EmptySched() : 
    # write expected schedule: keys are the 7 days of the week and values a a tuple of 24 False items (one for each hour)
    expected = {
        'Sunday'    : (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), 
        'Monday'    : (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), 
        'Tuesday'   : (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), 
        'Wednesday' : (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), 
        'Thursday'  : (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), 
        'Friday'    : (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), 
        'Saturday'  : (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)}
    # get schedule from class 
    recieved: dict = Params8229.BuildEmptySchedule()
    # check schedule keys
    if(expected.keys() != recieved.keys()): 
        return (False, ' - Schedule days-of-the-week keys are unexpected.')
    # check schedule values 
    for day, hours in expected.items() : 
        if(hours != recieved[day]) :
            return (False, ' - Hours for '+str(day)+' are unexpected.')
    # no issues 
    return (True, '')
    
    
def Test2_MatchInit() : 
    """Tests if the port argument given to a Params8229 object is correctly reflected in its GetInit() result. 

    Returns:
        tuple[bool,str]: Bool is true when the test passes, false otherwise. \\
            The string is an optional message. 
    """
    # create instance of Params8229 with valid arguments 
    param = Params8229(
            port            = 'COM1', 
            systemID        = 1, 
            motorDirection  = True, 
            motorSpeed      = 50, 
            randomReverse   = False, 
            mode            = 0, 
            reverseBaseTime = 5,
            reverseVarTime  = 10,
            schedule        = Params8229.BuildEmptySchedule(), 
            checkForValidParams = False
        )
    # get init build string
    paraminits = param.GetInit()
    # check that result matches expected 
    OUTexpectedInitStr: str = "PodApi.Parameters.Params8229(port='COM1', systemID=1, motorDirection=1, motorSpeed=50, randomReverse=False, reverseBaseTime=5, reverseVarTime=10, mode=0, schedule={'Sunday': (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), 'Monday': (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), 'Tuesday': (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), 'Wednesday': (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), 'Thursday': (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), 'Friday': (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), 'Saturday': (False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False)})"
    if(paraminits == OUTexpectedInitStr) :  return (True, '')
    return ( False, " - GetInit does not match given arguments.\n\tExpected: "+OUTexpectedInitStr+"\n\tRecieved: "+str(paraminits) )


def Test3_BadSystemID() : 
    """Tests if the Params8229 object correctly raises an Exception when it recieves a bad 'systemID' argument. 

    Returns:
        tuple[bool,str]: Bool is true when the test passes, false otherwise. \\
            The string is an optional message. 
    """
    try : 
        # create instance of Params8229
        param = Params8229(
            port            = 'COM1', 
            systemID        = -1, # 1, 
            motorDirection  = True, 
            motorSpeed      = 50, 
            randomReverse   = False, 
            mode            = 0, 
            reverseBaseTime = 5,
            reverseVarTime  = 10,
            schedule        = Params8229.BuildEmptySchedule(), 
            checkForValidParams = True
        )
        return (False, " - Params8229 did not notice the invalid 'systemID' argument.")
    except Exception as e : 
        return(True, '')   
    
def Test4_BadMotorSpeed() : 
    """Tests if the Params8229 object correctly raises an Exception when it recieves a bad 'motorSpeed' argument. 

    Returns:
        tuple[bool,str]: Bool is true when the test passes, false otherwise. \\
            The string is an optional message. 
    """
    try : 
        # create instance of Params8229
        param = Params8229(
            port            = 'COM1', 
            systemID        = 1, 
            motorDirection  = True, 
            motorSpeed      = 101, # 50, 
            randomReverse   = False, 
            mode            = 0, 
            reverseBaseTime = 5,
            reverseVarTime  = 10,
            schedule        = Params8229.BuildEmptySchedule(), 
            checkForValidParams = True
        )
        return (False, " - Params8229 did not notice the invalid 'motorSpeed' argument.")
    except Exception as e : 
        return(True, '') 
    
def Test5_BadMode() : 
    """Tests if the Params8229 object correctly raises an Exception when it recieves a bad 'mode' argument. 

    Returns:
        tuple[bool,str]: Bool is true when the test passes, false otherwise. \\
            The string is an optional message. 
    """
    try : 
        # create instance of Params8229
        param = Params8229(
            port            = 'COM1', 
            systemID        = 1, 
            motorDirection  = True, 
            motorSpeed      = 50, 
            randomReverse   = False, 
            mode            = 3, # 0
            reverseBaseTime = 5,
            reverseVarTime  = 10,
            schedule        = Params8229.BuildEmptySchedule(), 
            checkForValidParams = True
        )
        return (False, " - Params8229 did not notice the invalid 'mode' argument.")
    except Exception as e : 
        return(True, '') 
    
  
def Test6_BadReverseBaseTime() : 
    """Tests if the Params8229 object correctly raises an Exception when it recieves a bad 'reverseBaseTime' argument. 

    Returns:
        tuple[bool,str]: Bool is true when the test passes, false otherwise. \\
            The string is an optional message. 
    """
    try : 
        # create instance of Params8229
        param = Params8229(
            port            = 'COM1', 
            systemID        = 1, 
            motorDirection  = True, 
            motorSpeed      = 50, 
            randomReverse   = False, 
            mode            = 0, 
            reverseBaseTime = -5, # 5,
            reverseVarTime  = 10,
            schedule        = Params8229.BuildEmptySchedule(), 
            checkForValidParams = True
        )
        return (False, " - Params8229 did not notice the invalid 'reverseBaseTime' argument.")
    except Exception as e : 
        return(True, '') 
    
  
def Test7_BadReverseVarTime() : 
    """Tests if the Params8229 object correctly raises an Exception when it recieves a bad 'reverseVarTime' argument. 

    Returns:
        tuple[bool,str]: Bool is true when the test passes, false otherwise. \\
            The string is an optional message. 
    """
    try : 
        # create instance of Params8229
        param = Params8229(
            port            = 'COM1', 
            systemID        = 1, 
            motorDirection  = True, 
            motorSpeed      = 50, 
            randomReverse   = False, 
            mode            = 0, 
            reverseBaseTime = 5,
            reverseVarTime  = -10, # 10,
            schedule        = Params8229.BuildEmptySchedule(), 
            checkForValidParams = True
        )
        return (False, " - Params8229 did not notice the invalid 'reverseVarTime' argument.")
    except Exception as e : 
        return(True, '') 
    
def Test8_BadSchedule() : 
    """Tests if the Params8229 object correctly raises an Exception when it recieves a bad 'schedule' argument. 

    Returns:
        tuple[bool,str]: Bool is true when the test passes, false otherwise. \\
            The string is an optional message. 
    """
    try : 
        # create instance of Params8229
        param = Params8229(
            port            = 'COM1', 
            systemID        = 1, 
            motorDirection  = True, 
            motorSpeed      = 50, 
            randomReverse   = False, 
            mode            = 0, 
            reverseBaseTime = 5,
            reverseVarTime  = -10, # 10,
            schedule        = {'Bad' : (False,True)}, 
            checkForValidParams = True
        )
        return (False, " - Params8229 did not notice the invalid 'schedule' argument.")
    except Exception as e : 
        return(True, '') 
    