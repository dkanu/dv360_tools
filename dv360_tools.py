#########################
## Imports
#########################
import googleapiclient
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
from httplib2 import Http
from io import StringIO
import pandas
import datetime
#########################
## Helper Functions
#########################
def inj1(x, i, y):
	# Inject one string into another at a given index
	#	Args:
	#		x: string to accept injection
	#		i: index where injection will be applied
	#		y: string that will  e injected 
	#Ensure that injection is typed as a string 'str()' for use later on
    return x[:i] + str(y) + x[i:]
def fmt1(x):
	# Format additional audience list segments
	# Args:
	#	x: pandas series
	# Returns: sdf formatted audience list 
	return(' (({};););'.format(x))
def fmt2(x):
	# Format geographical location
	# Args:
	#	x: pandas series
	# Returns: sdf formatted geo list 
	return('{};'.format(x))
def ind1(x):
	# Return the length of a string plus 1. Used for injecting an additional AND statement in audience targeting
	# Args:
	#	x: pandas series
	# Returns: length of series plus 1
	return(len(x) + 1)
def StartDate():
	# Format start date to today enable SDF upload
	start_date = datetime.datetime.today() + datetime.timedelta(days=1)
	out = start_date.strftime("%m/%d/%Y") + str(" 0:00")
	return(out)	
def EndDate():
	# Format end date to thirty days ahead enable SDF upload
	end_date = datetime.datetime.today() + datetime.timedelta(days=30)
	out = end_date.strftime("%m/%d/%Y") + str(" 0:00")
	return(out)	
def empty1():
	#Return an empty string
	return('')
#########################
## API Request to fetch previously created templates from DV360
## Writing SDF Files using a modifier file to change audience or geography
#########################
def GetTemplate(key_file, io_id, write = False, write_name = 'template.csv'):
	# Get template lineitems with the option to write lineitems to file as SDF
	# Args:
	#	key_file: string indicating location of your Google service account credentials json keyfile
	#	io_id: integer of template DV360 insertion order id
	# Returns .csv file of sdf for line items in template DV360 insertion order
	scopes = ['https://www.googleapis.com/auth/doubleclickbidmanager']
	
	body={ # request information
	"fileTypes": ["LINE_ITEM"],
	"filterType":"INSERTION_ORDER_ID",
	"filterIds":[io_id],
	"version":"3.1",
	}
	credentials = ServiceAccountCredentials.from_json_keyfile_name(key_file, scopes = scopes)
	http_auth = credentials.authorize(Http())
	dbm = build('doubleclickbidmanager', 'v1', http=http_auth)
	request = dbm.sdf().download(body=body).execute() # api request
	
	if (write is True):
		with open(write_name, 'w') as f:
			f.write(request['lineItems'])
		f.close
	buffer = StringIO(request['lineItems'])
	return(buffer)
def WriteSDF(template, modifier, io_id, trow = 0, audience = True, geo = True):
	# Create new SDF from template and modifiers
	# Args:
	#	template: string indicating locations of the template file
	#	modifier: string indicating location of the modifier file
	#	io_id: string of insertion order id where line items will be uploaded
	#	trow: integer for the row corresponding to the lineitem to be used as a template
	#	audience: Boolean indicating whether audience lists will be modified
	#	geo: Boolean indicating whether geography will be modified
	# Writes new SDF file as csv
	sdf_out = pandas.read_csv(template)
	mod = pandas.read_csv(modifier, skipinitialspace=True, encoding='latin1')
	sdf_out = pandas.DataFrame(sdf_out.iloc[[trow]])
	template_row = sdf_out.iloc[trow]
	sdf_out = sdf_out.append([sdf_out]*(len(mod.index)-1), ignore_index=True)
	
	sdf_out['Line Item Id'] = [empty1()] * (len(sdf_out.index))
	sdf_out['Timestamp'] = [empty1()] * (len(sdf_out.index))
	sdf_out['Conversion Pixel Ids'] = [empty1()] * (len(sdf_out.index))
	sdf_out['Io Id'] = [io_id] * (len(sdf_out.index))
	sdf_out['Start Date'] = [StartDate()] * len(sdf_out.index)
	sdf_out['End Date'] = [EndDate()] * len(sdf_out.index)
	sdf_out['Name'] = mod['names']
	
	if(audience is True):
		# Audience formatting
		audience_targeting = sdf_out['Audience Targeting - Include']
		ind = list(map(ind1,audience_targeting ))
		injection = list(map(fmt1,mod['audience_list_id']))
		sdf_out['Audience Targeting - Include'] = list(map(inj1, audience_targeting, ind, injection))
	if(geo is True):
		# Geography formatting
		sdf_out['Geography Targeting - Include'] = list(map(fmt2,mod['geography_id']))
	with open('sdf_out.csv', 'w') as f:
		f.write(sdf_out.to_csv(index=False))
	f.close
#########################
## Function Calls
#########################
KEY_FILE = ''
MODIFIER_FILE = ''
TEMPLATE_INSERTION_ORDER_ID = 0000000
TARGET_INSERTION_ORDER_ID = 0000000
TEMPLATE_ROW_ID = 0

template_call = GetTemplate(KEY_FILE, TEMPLATE_INSERTION_ORDER_ID)
WriteSDF(template_call, MODIFIER_FILE, TARGET_INSERTION_ORDER_ID, TEMPLATE_ROW_ID, False, True)
