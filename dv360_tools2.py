from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
from httplib2 import Http
from io import StringIO
import pandas
import dv360_tools_helpers as dvt
import argparse
from distutils.util import strtobool

scopes = ['https://www.googleapis.com/auth/doubleclickbidmanager']
key = 'key.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(key, scopes=scopes)
http_auth = credentials.authorize(Http())
dbm = build('doubleclickbidmanager', 'v1', http=http_auth)


def get_template(io_id, write=False, write_name='template.csv'):
    """
    Access template IO line items
        Return as StringIO with option to write to file

    :param io_id: template
    :param write: bool; whether or not template gets written to file
    :param write_name: string; name of template file name
    :return: StringIO object;
    """

    # API Request Information
    body = {
        "fileTypes": ["LINE_ITEM"], "filterType": "INSERTION_ORDER_ID", "filterIds": [io_id], "version": "3.1", }
    request = dbm.sdf().download(body=body).execute()

    if write is True:
        with open(write_name, 'w') as f:
            f.write(request['lineItems'])
            f.close()

    buffer = StringIO(request['lineItems'])
    return buffer


def write_sdf(template, modifier, io_id, audience, geo, trow):
    """
    :param template: string; DV360 template Insertion Order ID
    :param modifier: string; modifier file name; should be included in the same directory as this file
    :param io_id: string; id of the insertion order you plan to upload the SDF to
    :param trow: integer; specific row to be used as template
    :param audience: bool; are you manipulating audience targeting - mutually exclusive w/ geo
    :param geo: bool; are you manipulating geography targeting - mutually exclusive w/ audience
    :return: None
    """

    sdf_out = pandas.read_csv(template)
    mod = pandas.read_csv(modifier, skipinitialspace=True, encoding='latin1')
    sdf_out = pandas.DataFrame(sdf_out.iloc[[trow]])
    sdf_out = sdf_out.append([sdf_out] * (len(mod.index) - 1), ignore_index=True)

    sdf_out['Line Item Id'] = [dvt.empty_string()] * (len(sdf_out.index))
    sdf_out['Timestamp'] = [dvt.empty_string()] * (len(sdf_out.index))
    sdf_out['Conversion Pixel Ids'] = [dvt.empty_string()] * (len(sdf_out.index))
    sdf_out['Io Id'] = [io_id] * (len(sdf_out.index))
    sdf_out['Start Date'] = [dvt.start_date()] * len(sdf_out.index)
    sdf_out['End Date'] = [dvt.end_date()] * len(sdf_out.index)
    sdf_out['Name'] = mod['names']

    if audience is True:
        """
        Audience Targeting Condition
        """
        audience_targeting = sdf_out['Audience Targeting - Include']
        ind = list(map(lambda x: len(x) + 1, audience_targeting))
        injection = list(map(dvt.format_audience, mod['audience_list_id']))
        sdf_out['Audience Targeting - Include'] = list(map(dvt.inject_string, audience_targeting, ind, injection))

    elif geo is True:
        """
        Geography Targeting Condition
        """
        sdf_out['Geography Targeting - Include'] = list(map(dvt.format_geo, mod['geography_id']))

    '''
    Pandas dataframe to CSV (SDF) File
    '''
    sdf_out.to_csv(path_or_buf='sdf_out.csv', index=False)


'''
Argument Parser
'''
parser = argparse.ArgumentParser(
 description='Generate SDF File from Template'
)

parser.add_argument(
    '-t',
    '--temp',
    nargs=1,
    metavar='',
    type=int,
    help='DV360 template Insertion Order ID'
)

parser.add_argument(
    '-m',
    '--modifier',
    nargs=1,
    metavar='',
    type=str,
    help='Modifier file name; should be included in the same directory as this file'
)

parser.add_argument(
    '-i',
    '--target_io',
    nargs=1,
    metavar='',
    type=str,
    help='id of the insertion order you plan to upload sdf to'
)

parser.add_argument(
    '-r',
    '--template_row',
    nargs=1,
    metavar='',
    type=int,
    help='specific row to be used as template'
)

parser.add_argument(
    '-a',
    '--audience',
    nargs=1,
    metavar='',
    type=lambda x: bool(strtobool(x)),
    help='are you manipulating audience targeting?'
)

parser.add_argument(
    '-g',
    '--geography',
    nargs=1,
    metavar='',
    type=lambda x: bool(strtobool(x)),
    help='are you manipulating geography targeting?'
)

args = parser.parse_args()

if __name__ == '__main__':
    template_call = get_template(args.temp[0])
    write_sdf(template=template_call, modifier=args.modifier[0], io_id=args.target_io[0],
              trow=args.template_row[0], audience=args.audience[0], geo=args.geography[0])
