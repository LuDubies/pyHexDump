"""This module contains functions used for generating the report."""

# MIT License
#
# Copyright (c) 2022 Andreas Merkle (web@blue-andi.de)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

################################################################################
# Imports
################################################################################
from pyHexDump.mem_access import mem_access_get_api_by_data_type
from pyHexDump.cmd_checksum import calc_checksum

################################################################################
# Variables
################################################################################

################################################################################
# Classes
################################################################################

################################################################################
# Functions
################################################################################

def _macros_compare_values(set_value, actual_value, value_format="{:02X}"):
    """Compares the set_value and the actual_value.

        Args:
            set_value(int): Set value
            actual_value(int): Actual value
            value_format (str, optional): The output format. Defaults to "{:02X}".

        Returns:
            "Not Ok (Set: <set_value>, Actual: <actual_value>)" if the set_value
            differs from the actual_value. Otherwise "Ok".
    """
    if set_value == actual_value:
        return "Ok"

    return f"Not Ok (Set: {value_format.format(set_value)}, " \
              f"Actual: {value_format.format(actual_value)})"

def _macros_convert_middle_to_little_endian(value):
    """Converts the value from middle to little endian representation.
        The value 0xCCDDAABB should be represented as 0xAABBCCDD

        Args:
            value(int): Value in middle endian representation

        Retruns:
            Value in little endian representation
    """
    result = 0

    # Shift CCDD to the right position
    result = (value << 16) & 0xFFFFFFFF

    # Shift AABB to the right position
    result |= (value >> 16) & 0xFFFFFFFF

    return result

def _macros_check_stadabm(value):
    """Checks if the passed value is word alligned and if the address
       is inside PFLASH (Compare chapter 2 of the Aurix datasheet).

        Args:
            value(int): Address to check

        Returns:
            "Ok" if the value is valid, otherwise "Not Ok <error-reason>"
    """
    segment_8_pflash = range(0x80000000, 0x811FFFFF)
    segment_10_pflash = range(0xA0000000, 0XA11FFFFF)
    if value in segment_8_pflash or value in segment_10_pflash:
        # Check if it is word alligned - 32bit system
        if value%4:
            return "Not Ok (STADABM is not word alligned)"
        else:
            return "Ok"
    else:
        return "Not Ok (STADABM is not in the PFLASH)"

def get_macro_dict():
    """Get the macro dictionary. The macros will be supported inside the template
        and can be used there.

    Returns:
        dict: Macro dictionary
    """
    macro_dict = {}

    macro_dict["macros_compare_values"] = _macros_compare_values
    macro_dict["macros_check_stadabm"] = _macros_check_stadabm
    macro_dict["mem_access_get_api_by_data_type"] = mem_access_get_api_by_data_type
    macro_dict["calc_checksum"] = calc_checksum
    macro_dict["convert_middle_to_little_endian"] = _macros_convert_middle_to_little_endian
    macro_dict["bootloader_start_addr"] = 0x000000

    return macro_dict

################################################################################
# Main
################################################################################