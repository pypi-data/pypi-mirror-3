#   PyCOM - Distributed Component Model for Python
#   Copyright (c) 2011-2012, Dmitry "Divius" Tantsur
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are
#   met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the following disclaimer
#     in the documentation and/or other materials provided with the
#     distribution.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#   "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#   LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#   A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#   OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#   DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#   THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#   (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Synchronous client API for PyCOM nameserver."""

import zmq

from . import conf, constants, exceptions, interfaces, invoke, protocol


def nameserver():
    """Get nameserver invoker."""
    global _nameserver

    if _nameserver is not None:
        return _nameserver

    ns_conf = conf.configuration.get("nameserver", constants.NS_NAME_LOCAL)
    if ns_conf == constants.NS_NAME_LOCAL:
        try:
            ns_class = interfaces.registry[constants.IFACE_NAMESERVER]
        except KeyError:
            ns_class = None

        if ns_class is not None:
            _nameserver = invoke.DirectInvoker(ns_class())
        else:
            raise exceptions.ServiceNotFound("Nameserver not found")
    else:
        _nameserver = _detect_ns(ns_conf)

    return _nameserver


def locate(iface):
    """Locate a service providing given interface."""
    ns_invoker = nameserver()
    try:
        info = ns_invoker.invoke(constants.NS_METHOD_LOCATE,
            {"interface": iface})
    except exceptions.RemoteError as err:
        if err.code == constants.ERROR_SERVICE_NOT_FOUND:
            raise exceptions.ServiceNotFound(
                "Service with interface '%s' not found" % iface)
        else:
            raise

    return invoke.RemoteInvoker(info["address"], iface)


# Private

_nameserver = None


def _detect_ns(host):
    """Detect nameserver on a given host."""
    sock = protocol.context.socket(zmq.REQ)
    try:
        sock.connect(host)
    except zmq.ZMQError as err:
        sock.close(linger=0)
        if err.errno == zmq.EINVAL:
            raise exceptions.ConfigurationError(
                "Invalid nameserver address: %s" % host)
        else:
            raise exceptions.ServiceNotFound("Nameserver not available")

    try:
        protocol.send_request(sock, constants.IFACE_NAMESERVER,
            constants.NS_METHOD_STAT, None,
            timeout=constants.PROTO_DEFAULT_TIMEOUT)
    except exceptions.ServiceNotAvailable:
        sock.close(linger=0)
        raise exceptions.ServiceNotFound("Nameserver not available")

    return invoke.RemoteInvoker(sock, constants.IFACE_NAMESERVER)
