Project Status
===============

Known Issues
-------------

- `Issue 1 <https://bitbucket.org/divius/pycom/issue/1>`_
  Nameserver stores any registered record forever (until restart).
- `Issue 2 <https://bitbucket.org/divius/pycom/issue/2>`_
  pycom.launcher lacks tests
- `Issue 3 <https://bitbucket.org/divius/pycom/issue/3>`_
  RemoteInvoker fails if service is restarted
- `Issue 4 <https://bitbucket.org/divius/pycom/issue/4>`_
  Nameserver should disallow service rewriting

Future Ideas
-------------

General
++++++++

#. Binary data support.
   Offers possibility to transfer several binary data blocks along with
   JSON data. Server example::

    import pycom

    @pycom.interface("...")
    class MyInterface(object):

        @pycom.method("...")
        def method(self, request):
            for file_obj in request.files:
                pass  # file_obj is NamedTemporaryFile here
            return {}, pycom.Binary("/etc/passwd")

   or::

    import io
    import pycom

    @pycom.interface("...")
    class MyInterface(object):

        @pycom.method("...")
        def method(self, request):
            out1 = io.BytesIO()
            # ...
            return {}, pycom.Binary(out1), pycom.Binary(out2)

   Client::

    import pycom
    pycom.configure(nameserver="...")

    service = pycom.locate("...")
    result, files = service.invoke("...", {}, with_binary=True)
    for file_obj in files:
        pass  # file_obj is NamedTemporaryFile here

API Extensions
+++++++++++++++

#. Proxy extension.
   Provides tighter integration with Python language, e.g.::

    import pycom
    pycom.configure(nameserver="...")

    from pycom.ext.proxy import locate, proxy
    ns = proxy(pycom.nameserver())
    ns = ns.locate(interface="org.pycom.nameserver")  # Keyword arguments instead of JSON
    for service_info in ns.list_services():           # directly use remote method name
        print service_info

#. PUB-SUB extension.
   Provides publisher-subscriber pattern for services, e.g.::

    import pycom
    pycom.configure(nameserver="...")

    from pycom.ext.pubsub import publisher

    # Publish random number every second
    @publisher("demo.interface.name")
    def pub_demo():
        while True:
            yield random.random()
            time.sleep(1)

   Client::

    import pycom
    pycom.configure(nameserver="...")

    from pycom.ext.pubsub import subscriber

    client = subscriber("demo.interface.name")
    print client[:10] # Print 10 random numbers in 10 seconds

#. Workflow extension.
   Acts as a separate service, provides API for managing chains of calls
   to different services. Client example::

    import pycom
    pycom.configure(nameserver="...")

    from pycom.ext.workflow import workflow

    w = workflow("/demo/workflow/1")  # Notice service name, not interface name
    result = w.invoke("task1", ...)   # Now w acts like any component

   Example configuration::

    {
        "tasks": {
            "task1": [
                {"interface": "demo.interface.1"},
                {"interface": "demo.interface.2"},
                {"interface": "demo.interface.3"}
            ]
        }
    }

#. Access extension.
   Manages access control for interfaces or methods, e.g.::

    import pycom
    from pycom.ext import access

    @access.auth(access.PasswordFile("/etc/passwd"))
    @pycom.interface("...")
    class MyInterface(object): pass

   or::

    import pycom
    from pycom.ext import access

    @pycom.interface("...")
    class MyInterface(object):

        @access.auth(access.PasswordFile("/etc/passwd"))
        @pycom.method("...")
        def method(self, request): pass

Other
++++++

- Replication for nameservers
