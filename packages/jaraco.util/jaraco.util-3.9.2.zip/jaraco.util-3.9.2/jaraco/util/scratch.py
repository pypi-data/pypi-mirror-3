from __future__ import print_function
import ctypes

class SYSTEMTIME(ctypes.Structure):
	_fields_ = [
		('year', ctypes.c_ushort),
		('month', ctypes.c_ushort),
		('day_of_week', ctypes.c_ushort), 
		('day', ctypes.c_ushort), 
		('hour', ctypes.c_ushort), 
		('minute', ctypes.c_ushort), 
		('second', ctypes.c_ushort), 
		('millisecond', ctypes.c_ushort), 
	]

class TIME_ZONE_INFORMATION(ctypes.Structure):
	_fields_ = [
		('bias', ctypes.c_long),
		('standard_name', ctypes.c_wchar*32),
		('standard_date', SYSTEMTIME),
		('standard_bias', ctypes.c_long),
		('daylight_name', ctypes.c_wchar*32),
		('daylight_date', SYSTEMTIME),
		('daylight_bias', ctypes.c_long),
	]

def GetTimeZoneInformation(name=None):
	tzi = TIME_ZONE_INFORMATION()
	if name: tzi.standard_name = name
	ctypes.windll.kernel32.GetTimeZoneInformation(ctypes.byref(tzi))
	return tzi

if __name__=='__main__':
	tzi = GetTimeZoneInformation('EST')
	print(tzi)