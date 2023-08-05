Summary
=======

    VxRPC implements XML-RPC client. It is based on xmlrpc-c_ client library
    with cURL_ transport. The implementation is faster, than standard xmlrpclib
    at least in 10 times.

Example of usage
================

    ::

        #!/usr/bin/env python

        import vxrpc

        try:
            rpc_call = vxrpc.Caller('http://your_rpc_server')
            response = rpc_call('Id::get_session', login='user')
        except vxrpc.Exception as e:
            print e.message

.. _xmlrpc-c: http://xmlrpc-c.sourceforge.net/
.. _cURL: http://curl.haxx.se/
