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

from misc cimport const_char_ptr, time_t

cdef extern from "structsize.h":
    size_t xmlrpc_cxpsize_user_agent()
    size_t xmlrpc_cpsize_transportparm_size()


cdef extern from "xmlrpc-c/util.h":
    ctypedef struct xmlrpc_env:
        int fault_occurred
        int fault_code
        char * fault_string

    void xmlrpc_env_init(xmlrpc_env *)
    void xmlrpc_env_clean(xmlrpc_env *)


cdef extern from "xmlrpc-c/base.h":
    struct xmlrpc_value "_xmlrpc_value":
        pass

    ctypedef enum xmlrpc_type:
        XMLRPC_TYPE_INT,
        XMLRPC_TYPE_BOOL,
        XMLRPC_TYPE_DOUBLE,
        XMLRPC_TYPE_DATETIME,
        XMLRPC_TYPE_STRING,
        XMLRPC_TYPE_BASE64,
        XMLRPC_TYPE_ARRAY,
        XMLRPC_TYPE_STRUCT,
        XMLRPC_TYPE_C_PTR,
        XMLRPC_TYPE_NIL,
        XMLRPC_TYPE_I8

    xmlrpc_type xmlrpc_value_type(xmlrpc_value*)
    const_char_ptr xmlrpc_type_name(xmlrpc_type)

    void xmlrpc_DECREF(xmlrpc_value *)
    xmlrpc_value * xmlrpc_nil_new(xmlrpc_env *)
    xmlrpc_value * xmlrpc_array_new(xmlrpc_env *)
    xmlrpc_value * xmlrpc_struct_new(xmlrpc_env *)
    void xmlrpc_array_append_item(xmlrpc_env *, xmlrpc_value *, xmlrpc_value *)
    int xmlrpc_struct_size(xmlrpc_env *, xmlrpc_value *)

    void xmlrpc_struct_read_member(xmlrpc_env *, xmlrpc_value *,
            unsigned int, xmlrpc_value **, xmlrpc_value **)

    void xmlrpc_read_string(xmlrpc_env *, xmlrpc_value *, char **)
    void xmlrpc_read_int(xmlrpc_env *, xmlrpc_value *, int *)
    void xmlrpc_read_double(xmlrpc_env *, xmlrpc_value *, double *)
    void xmlrpc_read_bool(xmlrpc_env *, xmlrpc_value *, int *)
    void xmlrpc_read_datetime_sec(xmlrpc_env *, xmlrpc_value *, time_t *)

    int xmlrpc_array_size(xmlrpc_env *, xmlrpc_value *)

    void xmlrpc_array_read_item(xmlrpc_env *, xmlrpc_value *,
            unsigned int, xmlrpc_value **)

    xmlrpc_value * xmlrpc_build_value(xmlrpc_env *, const_char_ptr, ...)
    void xmlrpc_struct_set_value(xmlrpc_env *, xmlrpc_value *,
            const_char_ptr, xmlrpc_value *)


cdef extern from "xmlrpc-c/client.h":
    struct xmlrpc_client:
        pass

    struct xmlrpc_curl_xportparms:
        int no_ssl_verifypeer
        int no_ssl_verifyhost
        const_char_ptr user_agent

    struct xmlrpc_clientparms:
        const_char_ptr transport
        xmlrpc_curl_xportparms transportP
        void * transportparmsP
        size_t transportparm_size

    void xmlrpc_client_create(xmlrpc_env *, int, const_char_ptr,
            const_char_ptr, xmlrpc_clientparms *, unsigned int, xmlrpc_client **)

    void xmlrpc_client_destroy(xmlrpc_client *)
    void xmlrpc_client_setup_global_const(xmlrpc_env *)

    ctypedef struct xmlrpc_server_info:
        pass

    xmlrpc_server_info * xmlrpc_server_info_new(xmlrpc_env *, const_char_ptr)
    void xmlrpc_server_info_free(xmlrpc_server_info *)

    void xmlrpc_client_call2(xmlrpc_env *, xmlrpc_client *, xmlrpc_server_info *,
                        const_char_ptr, xmlrpc_value *, xmlrpc_value **)

cdef extern from "xmlrpc-c/client_global.h":
    int XMLRPC_CLIENT_NO_FLAGS

