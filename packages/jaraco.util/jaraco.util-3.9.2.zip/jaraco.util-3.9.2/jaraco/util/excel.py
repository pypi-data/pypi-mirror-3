#!python

# $Id$

import tempfile
import os
from win32com.client import GetObject, Dispatch

# constants from http://msdn.microsoft.com/en-us/library/bb241279.aspx
xlXMLSpreadsheet = 46

def GetExcelWorkbookAsXML(path):
	"""
	Use Office 2003 or Office 2007 to open up a .xls workbook, save
	it as the Office 2003 Excel XML Spreadsheet format in a temporary
	file, read that XML into memory, then delete the temporary file.
	"""
	app = Dispatch('Excel.Application')
	wb = app.Workbooks.Open(path)
	tempfile_descriptor, tempfile_name = tempfile.mkstemp(suffix='.xml')
	os.close(tempfile_descriptor)
	os.remove(tempfile_name)
	wb.SaveAs(Filename=tempfile_name, FileFormat=xlXMLSpreadsheet)
	wb.Close(SaveChanges=0)
	app.Quit()
	del app
	data = open(tempfile_name, 'rb').read()
	os.remove(tempfile_name)
	return data