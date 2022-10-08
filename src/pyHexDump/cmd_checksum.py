"""Command to calculate the checksum.
The algrotihm and the table are taken from https://github.com/Michaelangel007/crc32
or from http://ross.net/crc/download/crc_v3.txt."""

# MIT License
#
# Copyright (c) 2022 Tobias Stelze (tobias.stelzle@newtec.de)
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
from pyHexDump.constants import Ret
from pyHexDump.common import common_load_binary_file, common_print_value
from pyHexDump.mem_access import MemAccessU8

################################################################################
# Variables
################################################################################

_CMD_NAME = "checksum"

################################################################################
# Classes
################################################################################

################################################################################
# Functions
################################################################################

def calc_checksum(binary_data, start_address, end_address,\
    polynomial, bit_width, seed, reverse_input, reverse_output, final_xor):
    """Calcuate the checksum for the given address in the binary_data and the
    given number of bytes.

    Args:
        binary_data (IntelHex): Binary data
        start_address (int): Address where to start the calculation
        end_address (int):  Address where to end the calculation (not included)
        polynomial(int): Generator polynomial to use in the CRC calculation.
                         The bits in this integer are to coefficients in the polynomial.
        bit_width(int): Number of bits for the CRC calculation. They have to match with
                        the generator polynomial
        seed (int): Seed value for the CRC calculation
        reverse_input(bool): Reflect each single input byte if True
        reverse_output(bool): Reflect the final CRC value if True
        final_xor(bool): Xor the final result with the value 0xff before returning the soulution

    Returns:
        Ret, checksum: Status information and checksum
    """
    ret_status = Ret.OK
    mem_access = MemAccessU8()

    offset = 0
    count = (end_address - start_address) / mem_access.get_size()

    # Valid bit widths: 8, 16, 32
    if (bit_width != 8) and (bit_width != 16) and (bit_width != 32):
        ret_status = Ret.ERROR_CRC_CACLULATION
        return ret_status, 0

    # The number to calculate the CRC has to be a multiple of word size
    if (end_address - start_address) % mem_access.get_size() != 0:
        ret_status = Ret.ERROR_CRC_CACLULATION
        return ret_status, 0

    bit_width_mask = pow(2, bit_width) - 1
    msb_mask = 1 << bit_width
    crc = seed
    word = 0

    polynomial = (1 << bit_width) | polynomial

    while count > 0:
        count -= 1

        word = mem_access.get_value(binary_data, start_address + offset)

        if reverse_input:
            tmp = f"{word:08b}"
            word = int(tmp[::-1], 2)

        crc = crc ^ (word << (bit_width - 8))

        for _ in range(8):
            crc = crc << 1

            if (crc & msb_mask) != 0:
                crc = crc ^ polynomial

        offset += mem_access.get_size()

    crc &= bit_width_mask

    if reverse_output:
        tmp = f"{word:0{bit_width}b}"
        word = int(tmp[::-1], 2)

    if final_xor:
        crc = crc ^ bit_width_mask

    return ret_status, crc

def _cmd_checksum(binary_file, start_address, end_address, \
    polynomial, bit_width, seed, reverse_input, reverse_output, final_xor):
    """Print the checksum for the given address and the given number of bytes
    to the console.

    Args:
        binary_file (str): File name of the binary file
        start_address (int): Address where to start the calculation
        end_address (int):  Address where to end the calculation (not included)
        polynomial(int): Generator polynomial to use in the CRC calculation.
                         The bits in this integer are to coefficients in the polynomial.
        bit_width(int): Number of bits for the CRC calculation. They have to match with
                        the generator polynomial
        seed (int): Seed value for the CRC calculation
        reverse_input(bool): Reflect each single input byte if True
        reverse_output(bool): Reflect the final CRC value if True
        final_xor(bool): Xor the final result with the value 0xff before returning the soulution

    Returns:
        Ret: If successful it will return OK, otherwise a corresponding error code.
    """
    ret_status, intel_hex = common_load_binary_file(binary_file)

    if ret_status == Ret.OK:
        ret_status, checksum = calc_checksum(intel_hex, start_address, end_address, \
            polynomial, bit_width, seed, reverse_input, reverse_output, final_xor)

    if ret_status == Ret.OK:
        value_width = bit_width // 4
        value_format = "{:0" + str(value_width) + "X}"
        common_print_value(checksum, value_format)

    return ret_status

def _exec(args):
    """Determine the required parameters from the program arguments and execute the command.

    Args:
        args (obj): Program arguments

    Returns:
        Ret: If successful, it will return Ret.OK otherwise a corresponding error.
    """
    return _cmd_checksum(args.binaryFile[0], \
                         args.saddr, args.eaddr,\
                         args.polynomial, args.bitWidth, \
                         args.seed, args.reverseIn, \
                         args.reverseOut, args.finalXOR)

def cmd_checksum_register(arg_sub_parsers):
    """Register the command specific CLI argument parser and get command
        specific paramters.

    Args:
        arg_sub_parsers (obj): Register the parser here

    Returns:
        obj: Command parameters
    """
    cmd_par_dict = {}
    cmd_par_dict["name"] = _CMD_NAME
    cmd_par_dict["execFunc"] = _exec

    parser = arg_sub_parsers.add_parser(
        "checksum",
        help="Calculate the CRC32 checksum for the specified data."
    )

    parser.add_argument(
        "binaryFile",
        metavar="BINARY_FILE",
        type=str,
        nargs=1,
        help="Binary file in intel hex format (.hex) or binary (.bin)."
    )
    parser.add_argument(
        "-sa",
        "--saddr",
        metavar="SADDR",
        type=lambda x: int(x, 0), # Support "0x" notation
        required=True,
        help="The calculation starts at this address."
    )
    parser.add_argument(
        "-ea",
        "--eaddr",
        metavar="EADDR",
        type=lambda x: int(x, 0), # Support "0x" notation
        required=True,
        help="The calculation ends at this address. (not included)"
    )
    parser.add_argument(
        "-p",
        "--polynomial",
        metavar="POLYNOMIAL",
        type=lambda x: int(x, 0), # Support "0x" notation
        required=False,
        default=0x04C11DB7,
        help="The polynomial for the CRC calculation.\nDefault: 0x04C11DB7"
    )
    parser.add_argument(
        "-bw",
        "--bitWidth",
        metavar="BIT_WIDTH",
        type=lambda x: int(x, 0), # Support "0x" notation
        required=False,
        default=32,
        help="The bit width of the CRC calculation.\nDefault: 32"
    )
    parser.add_argument(
        "-s",
        "--seed",
        metavar="SEED",
        type=lambda x: int(x, 0), # Support "0x" notation
        required=False,
        default=0,
        help="The seed value for the CRC calculation.\nDefault: 0"
    )
    parser.add_argument(
        "-ri",
        "--reverseIn",
        action="store_true",
        required=False,
        default=False,
        help="Use reverse input.\nDefault: False"
    )
    parser.add_argument(
        "-ro",
        "--reverseOut",
        action="store_true",
        required=False,
        default=False,
        help="Use reverse output.\nDefault: False"
    )
    parser.add_argument(
        "-fx",
        "--finalXOR",
        action="store_true",
        required=False,
        default=False,
        help="Use a final XOR with all bits 1.\nDefault: False"
    )

    return cmd_par_dict

################################################################################
# Main
################################################################################