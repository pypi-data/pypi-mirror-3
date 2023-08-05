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

Future Ideas
-------------

#. Proxy extension `pycom.ext.proxy`.
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
    result = w.invoke("task1", ...)   # Now w acts like any invoker

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
