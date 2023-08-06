#! -*- coding: utf-8 -*-

import os
import sys
from nose.tools import assert_dict_equal
sys.path.insert(0, os.path.abspath('..'))

import procinfo


def test_return_human_readable():
    assert_dict_equal(procinfo.return_human_readable(3035918336L), {'value': 2.83, 'str': '2.83 GB'})

