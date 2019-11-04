import datetime

"""
Helper Functions
"""
def inject_string(string_input, index, injection):
    """
    Inject one string into another at a given index
    :param string_input: string to accept injections
    :param index: index where injection will be applied
    :param injection: string that will be injected
    :return: string
    """
    return string_input[:index] + str(injection) + string_input[index:]


def format_audience(list_id):
    """
    Format audience list segment for use within an SDF
    :param list_id: string; corresponds to DV360 audience list id
    :return: string; formatted for SDF usage
    """
    return ' (({};););'.format(list_id)


def format_geo(geography_id):
    """
    Format geography id for use within an SDF
    :param geography_id: string; corresponds to DV360 geography id
    :return: string; formatted for SDF usage
    """

    return '{};'.format(geography_id)


def start_date():
    """
    Format tomorrow as SDF start date
    :return: string; representing date time of the start of the next day
    """
    start_date = datetime.datetime.today() + datetime.timedelta(days=1)
    return start_date.strftime("%m/%d/%Y") + str(" 0:00")


def end_date():
    """Format 30 days ahead as SDF end date
    :return: string; representing date time 30 days ahead
    """
    end_date = datetime.datetime.today() + datetime.timedelta(days=30)
    return end_date.strftime("%m/%d/%Y") + str(" 0:00")


def empty_string():
    """
    Return an empty string
    :return: string;
    """
    return ''
