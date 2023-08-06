import httplib

def get_status_code(host, path=""):
    """ This function retreives the status code of a website by requesting
        HEAD data from the host. This means that it only requests the headers.
        If the host cannot be reached or something else goes wrong, it returns
        None instead.
    """
    try:
        conn = httplib.HTTPConnection(host)
        conn.request("GET", path)
        return conn.getresponse().status
    except StandardError:
        return None

