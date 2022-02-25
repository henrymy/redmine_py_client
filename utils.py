#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
from datetime import date, timedelta
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate
import os
import smtplib
import yaml

from redminelib import Redmine, exceptions


def load_conf(path,filename):
    with open(path + '/'+ filename, 'r') as f:
        config = yaml.safe_load(f)
    return config

