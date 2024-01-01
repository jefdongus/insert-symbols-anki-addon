"""
Parses Anki's version. Uncommment and run this directly to evaluate test cases.
"""

import re
import pkgutil

import anki

""" Constants """

ANKI_VER_PRE_2_1_0 = 0
ANKI_VER_PRE_2_1_41 = 1
ANKI_VER_PRE_23_10 = 2
ANKI_VER_LATEST = 3

PYQT_VER_4 = 4
PYQT_VER_5 = 5
PYQT_VER_LATEST = 6

""" Parse Anki Version """

def _parse_anki_version_new():
    """ 
    pointVersion() is added in Anki 2.1.20 so if this gets called, by default 
    Anki is 2.1.20 or higher.
    """
    point_version = anki.utils.pointVersion()
    if point_version < 41:
        return ANKI_VER_PRE_2_1_41
    elif point_version < 231000:
        return ANKI_VER_PRE_23_10
    else:
        return ANKI_VER_LATEST

def _parse_anki_version_old():
    """
    This will only get called if Anki is between 2.0 and 2.1.19
    """
    try:
        version = anki.version
        v = tuple(map(int, re.match("(\d+)\.(\d+)\.(\d+)", version).groups()))

        if v[0] < 2:
            return ANKI_VER_PRE_2_1_0
        elif v[0] == 2 and v[1] < 1:
            return ANKI_VER_PRE_2_1_0
        else:
            return ANKI_VER_PRE_2_1_41
    except:
        return ANKI_VER_PRE_2_1_41

def get_anki_version():
    has_point_version = getattr(anki.utils, 'pointVersion', None)
    if has_point_version:
        return _parse_anki_version_new()
    else:
        return _parse_anki_version(version)


""" Obtain PyQt Version """

def get_pyqt_version():
    if pkgutil.find_loader('PyQt4'):
        return PYQT_VER_4
    elif pkgutil.find_loader('PyQt5'):
        return PYQT_VER_5
    else:
        return PYQT_VER_LATEST


""" Test Cases """

# def _test_version_parsing(version, expected):
#     if _parse_anki_version(version) == expected:
#         result = 'Passed'
#     else:
#         result = 'FAILED'
#     print("%s '%s'" % (result, version))

# _test_version_parsing('1.9.9', ANKI_VER_PRE_2_1_0)
# _test_version_parsing('2.0.31', ANKI_VER_PRE_2_1_0)
# _test_version_parsing('2.1.0', ANKI_VER_PRE_2_1_41)
# _test_version_parsing('2.1.4', ANKI_VER_PRE_2_1_41)
# _test_version_parsing('2.1.40', ANKI_VER_PRE_2_1_41)
# _test_version_parsing('2.1.40-beta', ANKI_VER_PRE_2_1_41)
# _test_version_parsing('2.1.41', ANKI_VER_LATEST)
# _test_version_parsing('2.1.41-beta', ANKI_VER_LATEST)
# _test_version_parsing('2.2.0', ANKI_VER_LATEST)
# _test_version_parsing('3.0.0', ANKI_VER_LATEST)
# _test_version_parsing('1.0', ANKI_VER_LATEST)
# _test_version_parsing('12345', ANKI_VER_LATEST)
# _test_version_parsing('abcde', ANKI_VER_LATEST)
