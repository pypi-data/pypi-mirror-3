# -*- coding:utf-8 -*-
from datetime import datetime
from email.Utils import formatdate


def rfc2822(d):
    """Converts a datetime to a RFC2822 compliant format.
    This format is required by iTunes"""
    return formatdate(float(d.strftime('%s')))

def parse_date(s):
    """Converts a timestamp received from YouTube to a python datetime"""
    return datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')
