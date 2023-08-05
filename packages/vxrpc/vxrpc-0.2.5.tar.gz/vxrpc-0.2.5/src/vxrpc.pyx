# encoding: utf-8
# Copyright (c) 2012 Volvox Development Team
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Author: Konstantin Lepa <konstantin.lepa@gmail.com>

from misc cimport const_char_ptr, memset, time_t
from xmlrpc_c cimport *
from libc.stdint cimport int32_t

import os

include "pyversion.pxi"
include "version.py"

IF PYTHON_VERSION >= 3:
    ctypedef str StringType
    cdef bytes str_to_bytes(StringType s):
        return s.encode('UTF-8')
    cdef StringType c_str_to_str(const_char_ptr c):
        return c.decode('UTF-8', 'strict')
    cdef bint isunicode(s):
        return isinstance(s, str)
ELSE:
    from cpython cimport unicode

    ctypedef bytes StringType
    cdef bytes str_to_bytes(StringType s):
        return s
    cdef StringType c_str_to_str(const_char_ptr c):
        return c
    cdef bint isunicode(s):
        return isinstance(s, unicode)


cdef int ver_number
cdef str VERSION_STR = __version__
cdef bytes VERSION_BT = str_to_bytes(VERSION_STR)
cdef str PACKAGE_STR = '/vxrpc'
cdef bytes PACKAGE_BT = str_to_bytes(PACKAGE_STR)
cdef bytes USER_AGENT = PACKAGE_BT + VERSION_BT

class Exception(__builtins__.Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class ValueTypeError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class BuildValueError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class DecomposeValueError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


cdef class Caller:
    """XML-RPC client class."""

    cdef xmlrpc_client *thisptr
    cdef xmlrpc_env env
    cdef xmlrpc_server_info *server_info
    cdef readonly str url
    cdef bint has_error

    cdef initialize(self):
        cdef xmlrpc_curl_xportparms curl_parms
        cdef xmlrpc_clientparms cli_parms

        self.thisptr = NULL
        self.server_info = NULL

        xmlrpc_env_init(&self.env)

        memset(&curl_parms, 0, sizeof(curl_parms))
        curl_parms.no_ssl_verifypeer = True
        curl_parms.no_ssl_verifyhost = True
        curl_parms.user_agent = USER_AGENT

        memset(&cli_parms, 0, sizeof(cli_parms))
        cli_parms.transport = 'curl'
        cli_parms.transportparmsP = &curl_parms
        cli_parms.transportparm_size = xmlrpc_cxpsize_user_agent()

        xmlrpc_client_create(&self.env, XMLRPC_CLIENT_NO_FLAGS,
                PACKAGE_BT, VERSION_BT, &cli_parms,
                xmlrpc_cpsize_transportparm_size(), &self.thisptr)

        if self.env.fault_occurred:
            self.has_error = True
            raise Exception(self.env.fault_string)

    cdef deinitialize(self):
        if self.thisptr is not NULL:
            xmlrpc_client_destroy(self.thisptr)
        if self.server_info is not NULL:
            xmlrpc_server_info_free(self.server_info)
        xmlrpc_env_clean(&self.env)

    def __cinit__(self):
        self.initialize()

    def __dealloc__(self):
        self.deinitialize()

    cdef init_server_info(self, url):
        self.server_info = xmlrpc_server_info_new(&self.env, url)
        if self.env.fault_occurred:
            self.has_error = True
            raise Exception(self.env.fault_string)

    def __init__(self, url):
        """x.__init__(url) -- set url of XML-RPC server."""
        self.has_error = False
        self.url = url
        self.init_server_info(url)

    cdef object convert_xmlrpc_value(self, xmlrpc_value *data):
        cdef xmlrpc_type data_type
        cdef object result
        cdef unsigned int idx
        cdef int size
        cdef xmlrpc_value *key
        cdef xmlrpc_value *value
        cdef xmlrpc_value *array
        cdef object key_obj
        cdef object value_obj
        cdef int int_value
        cdef double double_value
        cdef time_t time_value
        cdef const_char_ptr str_value

        data_type = xmlrpc_value_type(data)

        if data_type == XMLRPC_TYPE_STRING:
            xmlrpc_read_string(&self.env, data, &str_value)
            if self.env.fault_occurred:
                self.has_error = True
                raise DecomposeValueError(self.env.fault_string)
            result = c_str_to_str(str_value)
        elif data_type == XMLRPC_TYPE_STRUCT:
            size = xmlrpc_struct_size(&self.env, data)

            if self.env.fault_occurred:
                self.has_error = True
                raise DecomposeValueError(self.env.fault_string)

            result = {}
            for idx in range(size):
                xmlrpc_struct_read_member(&self.env, data, idx, &key, &value)
                if self.env.fault_occurred:
                    self.has_error = True
                    raise DecomposeValueError(self.env.fault_string)
                try:
                    xmlrpc_read_string(&self.env, key, &str_value)
                    if self.env.fault_occurred:
                        self.has_error = True
                        raise DecomposeValueError(self.env.fault_string)
                    key_obj = c_str_to_str(str_value)
                    value_obj = self.convert_xmlrpc_value(value)
                    result[key_obj] = value_obj
                finally:
                    xmlrpc_DECREF(key)
                    xmlrpc_DECREF(value)

        elif data_type == XMLRPC_TYPE_INT:
            xmlrpc_read_int(&self.env, data, &int_value)
            if self.env.fault_occurred:
                self.has_error = True
                raise DecomposeValueError(self.env.fault_string)
            result = int_value
        elif data_type == XMLRPC_TYPE_BOOL:
            xmlrpc_read_bool(&self.env, data, &int_value)
            if self.env.fault_occurred:
                self.has_error = True
                raise DecomposeValueError(self.env.fault_string)
            result = int_value
        elif data_type == XMLRPC_TYPE_DOUBLE:
            xmlrpc_read_double(&self.env, data, &double_value)
            if self.env.fault_occurred:
                self.has_error = True
                raise DecomposeValueError(self.env.fault_string)
            result = double_value
        elif data_type == XMLRPC_TYPE_DATETIME:
            xmlrpc_read_datetime_sec(&self.env, data, &time_value);
            if self.env.fault_occurred:
                self.has_error = True
                raise DecomposeValueError(self.env.fault_string)
            result = time_value
        elif data_type == XMLRPC_TYPE_ARRAY:
            size = xmlrpc_array_size(&self.env, data)
            if self.env.fault_occurred:
                self.has_error = True
                raise DecomposeValueError(self.env.fault_string)

            result = []
            for idx in range(size):
                xmlrpc_array_read_item(&self.env, data, idx, &value)
                if self.env.fault_occurred:
                    self.has_error = True
                    raise DecomposeValueError(self.env.fault_string)
                try:
                    value_obj = self.convert_xmlrpc_value(value)
                    result.append(value_obj)
                finally:
                    xmlrpc_DECREF(value)

        elif data_type == XMLRPC_TYPE_NIL:
            pass
        else:
            raise ValueTypeError('Unsupported value type: %s' % xmlrpc_type_name(data_type))

        return result

    cdef xmlrpc_value * convert_pyobject(self, object obj):
        cdef unsigned int idx
        cdef char *c_str
        cdef bytes bt_str
        cdef StringType key
        cdef xmlrpc_value *result
        cdef xmlrpc_value *value_v

        if isinstance(obj, (int, bool)):
            result = xmlrpc_build_value(&self.env, 'i', <int32_t>obj)
            if self.env.fault_occurred:
                self.has_error = True
                raise BuildValueError(self.env.fault_string)
        elif isinstance(obj, float):
            result = xmlrpc_build_value(&self.env, 'd', <double>obj)
            if self.env.fault_occurred:
                self.has_error = True
                raise BuildValueError(self.env.fault_string)
        elif isunicode(obj):
            bt_str = obj.encode('UTF-8')
            c_str = bt_str
            result = xmlrpc_build_value(&self.env, 's', c_str)
            if self.env.fault_occurred:
                self.has_error = True
                raise BuildValueError(self.env.fault_string)
        elif isinstance(obj, bytes):
            bt_str = obj
            c_str = bt_str
            result = xmlrpc_build_value(&self.env, 's', c_str)
            if self.env.fault_occurred:
                self.has_error = True
                raise BuildValueError(self.env.fault_string)
        elif isinstance(obj, dict):
            result = xmlrpc_struct_new(&self.env)
            if self.env.fault_occurred:
                self.has_error = True
                raise BuildValueError(self.env.fault_string)

            for key, value in obj.items():
                IF PYTHON_VERSION >= 3:
                    bt_str = key.encode('UTF-8')
                    c_str = bt_str
                ELSE:
                    c_str = key

                value_v = self.convert_pyobject(value)
                xmlrpc_struct_set_value(&self.env, result, c_str, value_v)
                if self.env.fault_occurred:
                    self.has_error = True
                    raise BuildValueError(self.env.fault_string)
                xmlrpc_DECREF(value_v)

        elif hasattr(obj, '__iter__') and not hasattr(obj, 'read'):
            result = xmlrpc_array_new(&self.env)
            if self.env.fault_occurred:
                self.has_error = True
                raise BuildValueError(self.env.fault_string)
            for elem in obj:
                value_v = self.convert_pyobject(elem)
                xmlrpc_array_append_item(&self.env, result, value_v)
                if self.env.fault_occurred:
                    self.has_error = True
                    raise BuildValueError(self.env.fault_string)
                xmlrpc_DECREF(value_v)
        else:
            raise ValueTypeError('Unsupported type of argument: %s', type(obj))

        return result

    cdef real_call(self, str method_name, tuple args, dict kwargs):
        cdef xmlrpc_value *params = NULL
        cdef xmlrpc_value *value = NULL
        cdef xmlrpc_value *result = NULL
        cdef int size
        cdef unsigned int idx

        params = xmlrpc_array_new(&self.env)
        if self.env.fault_occurred:
            self.has_error = True
            raise BuildValueError(self.env.fault_string)

        try:
            if not len(args) and not len(kwargs):
                value = xmlrpc_nil_new(&self.env)
                if self.env.fault_occurred:
                    self.has_error = True
                    raise BuildValueError(self.env.fault_string)
            else:
                for idx in range(len(args)):
                    value = self.convert_pyobject(args[idx])
                    try:
                        xmlrpc_array_append_item(&self.env, params, value)
                        if self.env.fault_occurred:
                            self.has_error = True
                            raise BuildValueError(self.env.fault_string)
                    finally:
                        xmlrpc_DECREF(value)
                value = self.convert_pyobject(kwargs)
                try:
                    xmlrpc_array_append_item(&self.env, params, value)
                    if self.env.fault_occurred:
                        self.has_error = True
                        raise BuildValueError(self.env.fault_string)
                finally:
                    xmlrpc_DECREF(value)

            response = None
            xmlrpc_client_call2(&self.env, self.thisptr,
                    self.server_info, method_name, params, &result)
            if self.env.fault_occurred:
                self.has_error = True
                raise Exception(self.env.fault_string)

            try:
                response = self.convert_xmlrpc_value(result)
            finally:
                xmlrpc_DECREF(result)
        finally:
            xmlrpc_DECREF(params)

        return response

    def __call__(self, method_name, *args, **kwargs):
        """x.__call__(method_name, *args, **kwargs) -- make XML-RPC call."""

        if self.has_error:
            self.deinitialize()
            self.initialize()
            self.init_server_info(self.url)
            self.has_error = False

        return self.real_call(method_name, args, kwargs)


cdef global_init():
    cdef xmlrpc_env env
    xmlrpc_env_init(&env)
    xmlrpc_client_setup_global_const(&env)
    if env.fault_occurred:
        raise Exception(env.fault_string)

global_init()

