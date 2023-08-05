import win32com.client as win32
import pythoncom
import pywintypes
from pywintypes import com_error
import winerror
from win32com.client import constants
import datetime

def ensure_excel_dispatch_support():
    """Ensure that early-bound dispatch support is generated for Excel typelib, version 1.7
    
    This may attempt to write to the site-packages directory"""
    try:
        win32.gencache.EnsureModule('{00020813-0000-0000-C000-000000000046}', 0, 1, 7)
    except Exception as e:
        raise Exception("Failed to verify / generate Excel COM wrappers. Check that you have write access to site-packages." + \
                        "See the original exception (in args[1]) for more info", e)

def marshal_to_excel_value(v):
    assert not (isinstance(v, list) or isinstance(v, tuple)), "marshal_to_excel_value only handles scalars" 

    if isinstance(v, datetime.datetime):
        return _datetime_to_com_time(v)
    else:
        return v

_com_time_type = type(pywintypes.Time(0))
def unmarshal_from_excel_value(v):
    assert not (isinstance(v, list) or isinstance(v, tuple)), "unmarshal_from_excel_value only handles scalars" 
    
    if isinstance(v, _com_time_type):
        return _com_time_to_datetime(v)
    else:
        return v

def _com_time_to_datetime(pytime):
    assert pytime.msec == 0, "fractional seconds not yet handled"
    return datetime.datetime(month=pytime.month, day=pytime.day, year=pytime.year, 
                             hour=pytime.hour, minute=pytime.minute, second=pytime.second)

def _datetime_to_com_time(dt):
    assert dt.microsecond == 0, "fractional seconds not yet handled"
    return pywintypes.Time( dt.timetuple() )


def enum_running_monikers():
    try:
        r = pythoncom.GetRunningObjectTable()
        for moniker in r:
            yield moniker
    except com_error as e:
        if e.args[0] == winerror.E_ACCESSDENIED:
            raise Exception("Access to the running object table was denied. This may be due to a high-privilege registered object")

# Searches the running object tablef or the workbook by filename
# None if not found
def get_running_xlWorkbook_for_filename(filename):
    # If we
    wbPartialMatch = None
    filename = filename.lower()
    context = pythoncom.CreateBindCtx(0)
    for moniker in enum_running_monikers():
        name = moniker.GetDisplayName(context, None).lower()      
        # name will be either a temp name "book1" or a full filename  "c:\temp\foo.xlsx"
        # use moniker.GetClassID() to narrow it down to a file Monikor?
        # match on full path, case insensitive
        if (filename == name):
            obj = pythoncom.GetRunningObjectTable().GetObject(moniker)
            wb = win32.Dispatch(obj.QueryInterface(pythoncom.IID_IDispatch))
            return wb
        # check for a partial match 
        if name.endswith('\\' + filename):
            obj = pythoncom.GetRunningObjectTable().GetObject(moniker)
            wbPartialMatch = win32.Dispatch(obj.QueryInterface(pythoncom.IID_IDispatch))
    
    # Didn't find a full match. Return partial match if we found one. 
    return wbPartialMatch

# Opens the workbook on disk.
def open_xlWorkbook(filename):
    excel = win32.gencache.EnsureDispatch('Excel.Application')
    excel.Visible = True
    return excel.Workbooks.Open(filename)

def get_open_xlWorkbooks():
    IID_Workbook = pythoncom.pywintypes.IID("{000208DA-0000-0000-C000-000000000046}")
    l = []
    for moniker in enum_running_monikers():
        obj = pythoncom.GetRunningObjectTable().GetObject(moniker)
        try:
            wb = win32.Dispatch(obj.QueryInterface(pythoncom.IID_IDispatch))
            # Python COM doesn't support QI for arbitrary interfaces, so we can't
            # just QI for IID_Workbook({000208DA-0000-0000-C000-000000000046})
            if (getattr(wb, "CLSID", None) == IID_Workbook):                
                l.append(wb)
        except com_error:
            pass
    return l