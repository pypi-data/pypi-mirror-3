This package enables communication between Python and Scratch using the
remote sensors feature of Scratch.

Remember to enable remote sensors in Scratch!  To do this:

1. Go to Sensing
2. Right-click on a 'sensor value'
3. Select 'enable remote sensor connections'

Example usage:

::

    import scratch
    s = scratch.Scratch()

    # to make a broadcast to scratch
    s.broadcast("from python")

    # to receive an update from scratch
    message = s.receive()
    # blocks until an update is received
    # message returned as  {'broadcast': [], 'sensor-update': {'scratchvar': '64'}}
    #                  or  {'broadcast': ['from scratch'], 'sensor-update': {}}
    # where scratchvar is the name of a variable in scratch
    # and 'from scratch' is the name of a scratch broadcast

    # send sensor updates to scratch
    data = {}
    data['pyvar'] = 123
    for data['pycounter'] in range(60):
        s.sensorupdate(data)

