connection discovery:
    name
    binding
    handler

connect(hostname, port, order):
    for method in order
        try:
            conn = method.handler()
            return method.binding(conn)
        except ConnectionDiscoveryFailed:
            log results
