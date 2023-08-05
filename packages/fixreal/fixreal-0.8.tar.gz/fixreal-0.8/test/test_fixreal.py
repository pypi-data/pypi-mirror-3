# coding=utf-8
"""
Tests designed to be run with nose after installation of the fixreal package
"""

from nose.tools import ok_, eq_, raises

import fixreal

R2FIX = []
F2REAL = []

def setup():
    R2FIX.append((-0.9921875, "fix_8_7", 129.0))
    R2FIX.append((-3.96875, "fix_8_5", 129.0))
    R2FIX.append((-127, "fix_8_0", 129.0))
    R2FIX.append((1.0078125, "ufix_8_7", 129.0))
    R2FIX.append((4.03125, "ufix_8_5", 129.0))
    R2FIX.append((129, "ufix_8_0", 129.0))
    F2REAL.append((0b10000001, "fix_8_7", -0.9921875))
    F2REAL.append((0b10000001, "fix_8_5", -3.96875))
    F2REAL.append((0b10000001, "fix_8_0", -127.0))
    F2REAL.append((0b10000001, "ufix_8_7", 1.0078125))
    F2REAL.append((0b10000001, "ufix_8_5", 4.03125))
    F2REAL.append((0b10000001, "ufix_8_0", 129.0))

def check_real2fix(arg):
    eq_(fixreal.real2fix(arg[0], fixreal.conv_from_name(arg[1])), arg[2])

def check_fix2real(arg):
    eq_(fixreal.fix2real(arg[0], fixreal.conv_from_name(arg[1])), arg[2])

def test_real2fix():
    for _rf in R2FIX:
        yield check_real2fix, _rf

def test_fix2real():
    for _rf in F2REAL:
        yield check_fix2real, _rf

@raises(fixreal.ConversionError)
def test_bit_error():
    fixreal.get_conv(15, 0, True)

@raises(fixreal.ConversionError)
def test_name_error():
    fixreal.conv_from_name("this is a wrong name!!!")

@raises(fixreal.ConversionError)
def test_sign_error():
    fixreal.real2fix(-10, fixreal.conv_from_name("ufix_32_0"))
