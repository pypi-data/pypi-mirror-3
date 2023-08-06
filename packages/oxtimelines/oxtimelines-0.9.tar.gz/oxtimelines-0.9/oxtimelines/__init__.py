# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
# GPL 2008-2010
__version__ = 'bzr'

import gobject
gobject.threads_init()

from glob import glob
import math
import os
import time

import pygst
pygst.require("0.10")
import gst
import Image

import timeline
from timeline import Timelines
