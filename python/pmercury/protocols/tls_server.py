#!/usr/bin/env python3

"""     
 Copyright (c) 2019 Cisco Systems, Inc. All rights reserved.
 License at https://github.com/cisco/mercury/blob/master/LICENSE
"""

import os
import sys
from sys import path
from binascii import hexlify

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/../')
from utils.tls_utils import *
from utils.tls_constants import *
from protocol import Protocol

MAX_CACHED_RESULTS = 2**24


class TLS_Server(Protocol):

    def __init__(self, fp_database=None, config=None):
        # populate fingerprint databases
        self.fp_db = {}


    @staticmethod
    def proto_identify(data, offset, data_len):
        if data_len-offset < 16:
            return False
        if (data[offset]    == 22 and
            data[offset+1]  ==  3 and
            data[offset+2]  <=  3 and
            data[offset+5]  ==  2 and
            data[offset+9]  ==  3 and
            data[offset+10] <=  3):
            return True
        return False


    @staticmethod
    def fingerprint(data, offset, data_len):
        offset += 5

        # extract handshake version
        fp_ = b'(%02x%02x)' % (data[offset+4],data[offset+5])

        # skip header/server_random
        offset += 38

        # parse/skip session_id
        session_id_length = data[offset]
        offset += 1 + session_id_length
        if offset >= data_len:
            return None, None

        # parse selected_cipher_suite
        fp_ += b'(%02x%02x)' % (data[offset],data[offset+1])
        offset += 2
        if offset >= data_len:
            return fp_+b'()', None

        # parse/skip compression method
        compression_methods_length = data[offset]
        offset += 1 + compression_methods_length
        if offset >= data_len:
            return fp_+b'()', None

        # parse/skip extensions length
        ext_total_len = int.from_bytes(data[offset:offset+2], 'big')
        offset += 2
        if offset >= data_len:
            return fp_+b'()', None

        # parse/extract/skip extension type/length/values
        fp_ += b'('
        while ext_total_len > 0:
            if offset >= data_len:
                return fp_+b')', None

            tmp_fp_ext, offset, ext_len = parse_extension(data, offset)
            fp_ += b'(%s)' % tmp_fp_ext

            ext_total_len -= 4 + ext_len
        fp_ += b')'

        return fp_, None


    def get_human_readable(self, fp_str_):
        lit_fp = eval_fp_str(fp_str_)

        fp_h = {}
        fp_h['version'] = get_version_from_str(lit_fp[0][0])
        fp_h['selected_cipher_suite'] = get_cs_from_str(lit_fp[1][0])[0]
        fp_h['extensions'] = []
        if len(lit_fp) > 2:
            fp_h['extensions'] = get_ext_from_str(lit_fp[2], mode='server')

        return fp_h
