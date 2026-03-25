import base64
import socket
import json
import argparse
import tarfile
import os
import glob
import logging
import select
import time

# Make a JSON RPC call to the specified method
def call_rpc(host, port, method, params, host_ip=None, rpc_callback_port=None, log = True, timeout = 3):
    # Store details in dictionary
    if method == "StartJobWithNotification":
        params.insert(0, rpc_callback_port)
        params.insert(0, host_ip)

    payload = {
        "method": method,
        "params": params,
        "jsonrpc": "2.0",
        "id": "1",
    }

    ret = _call_rpc(host=host, port=port, payload=payload, log=log, timeout=timeout)
    if isinstance(ret, str):
        ret = ret.strip()
    return ret


def _call_rpc(host, port, payload, log = True, timeout = 3): # 1800
    # TODO: timeout affects amount of data transferred, not jsut time.  We need to find a way to allow tons of data in a short time as well.
    
    # Make socket connection
    # print(datetime.datetime.now(), "call_rpc - timeout=",timeout)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connect_timeout = timeout
    if timeout > 3:
        connect_timeout = 3
    s.settimeout(connect_timeout)
    try:
        s.connect((host, port))
        # print(datetime.datetime.now(), "call_rpc - connected")
    except:
        print("Communication with DUT timed out.")
        return "TIMEOUT"

    # Convert to JSON and send
    request = json.dumps(payload)
    if log:
        logging.debug("sending RPC: " + str(request))
    s.sendall(request.encode('utf-8') + b'\r\n')

    # Loop retrieving port number until nothing more can be pulled from buffer
    # Using "select" allows a 1 sec interval to check for ctrl-c interrupts

    # Callback after 30 minutes
    # x = 0
    start_time = time.time()
    result = ""
    # while x <= int(timeout):
    while True:
        r, _, _ = select.select([s], [], [], 1.0)
        if r:
            res = s.recv(1024).decode()
            if res == "":
                break
            result += res
        if time.time() > (start_time + timeout):
            return "TIMEOUT"

    # if x >= int(timeout):
    #     return "CALLBACK"

    # Decode JSON result
    # output = json.loads(result)
    # print output
    # return output["result"]
    return result


def upload(host, port, source, dest):

    if len(glob.glob(source)) == 0:
        logging.error("ERROR:  Source path: " + source + ", not found!")

    # Store details in dictionary
    payload = {
        "method": "Upload",
        "params": [dest, True],
        "jsonrpc": "2.0",
        "id": "1",
    }

    file_port = _call_rpc(host, port, payload)
    output = json.loads(file_port)
    file_port = output["result"]

    # Make socket connection to file port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, file_port))

    # closing the tar record doesn't close sockfile
    # it need to be done manually (so hold a ref to it)
    sockfile = s.makefile("rwb")
    tf = tarfile.open(mode = "w|", fileobj = sockfile)

    for f in glob.glob(source):
        directory = os.path.dirname(os.path.abspath(f))
        filename = os.path.abspath(f).replace(directory + os.path.sep, "")
        tf.add(f, filename)

    tf.close()
    # result = ""
    # while True:
    result = s.recv(1024)
    #     if res == "":
    #         break
    #     result += res
    # print "UPLOAD RESULT: ", result

    # since we already have it, use sockfile readline to read until EOL
    # result = sockfile.readline()
    sockfile.close()
    s.close() #closing sockfile doesn't close underlying socket
    # print "UPLOAD RESULT: ", result


def download(host, port, source, dest):
    # Store details in dictionary
    payload = {
        "method": "Download",
        "params": [source],
        "jsonrpc": "2.0",
        "id": "1",
    }

    file_port = _call_rpc(host, port, payload)
    output = json.loads(file_port)
    file_port = output["result"][0]

    # Make socket connection to file port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, file_port))

    tf = tarfile.open(mode="r|", fileobj=s.makefile('rb', None))
    tf.extractall(path = dest)

    tf.close()


def plugin_load(host, port, dll_id, dll_class, dll_path):
    # Store details in dictionary
    payload = {
        "method": "PluginLoad",
        "params": [dll_id, dll_class, dll_path],
        "jsonrpc": "2.0",
        "id": "1",
    }
    result = _call_rpc(host, port, payload)
    return result


def plugin_call(host, port, dll_id, method, *arg):
    # Store details in dictionary
    payload = {
        "method":"PluginCallMethod",
        "params": [dll_id, method, *arg],
        "jsonrpc": "2.0",
        "id": "1",
    }
    result = _call_rpc(host, port, payload)
    return result


def plugin_screenshot(host, port, dll_id, x=0.0, y=0.0, w=1.0, h=1.0):
    # Store details in dictionary
    payload = {
        "method":"PluginCallMethod",
        "params": [dll_id, "Screenshot", x, y, w, h],
        "jsonrpc": "2.0",
        "id": "1",
    }
    result = _call_rpc(host, port, payload)
    # print("RESULT: " + result)
    result_dict = json.loads(result)
    data = result_dict["result"]
    img = base64.b64decode(data)
    return img


def plugin_screen_info(host, port, dll_id):
    # Store details in dictionary
    payload = {
        "method":"PluginCallMethod",
        "params": [dll_id, "GetScreenInfo"],
        "jsonrpc": "2.0",
        "id": "1",
    }
    result = _call_rpc(host, port, payload)
    # print("RESULT: " + result)
    result_dict = json.loads(result)
    data = result_dict["result"]
    # info = data.split(',')
    # width = int(info[0])
    # height = int(info[1])
    # scale = float(info[2])
    # return (width, height, scale)
    # Expected format: "width,height,scale;" for each monitor
    displays = data.rstrip(',;').split(';')
    if len(displays) == 0:
        print("ERROR: No displays found in plugin_screen_info()")
        return []
    for display in displays:
        info = display.split(',')
        if len(info) != 3:
            print("ERROR: Invalid display info format in plugin_screen_info()")
            return []
        # Expected format: "width,height,scale"
        if not (info[0].isdigit() and info[1].isdigit() and info[2].replace('.', '', 1).isdigit()):
            print("ERROR: Non-numeric values found in plugin_screen_info()")
            return []
    # Return displays in a list of tuples
    return [(int(info.split(',')[0]), int(info.split(',')[1]), float(info.split(',')[2])) for info in displays]


def get_job_result(host, port, jobid):
    # Store details in dictionary
    payload = {
        "method": "GetJobResultEx",
        "params": [jobid],
        "jsonrpc": "2.0",
        "id": "1",
    }
    result = _call_rpc(host, port, payload)
    # output = json.loads(result)
    # file_port = output["result"]
    return result


if __name__ == "__main__":
    # Define command line arguments
    parser = argparse.ArgumentParser(description='This is a client for sending JSON RPC requests to a server.')
    parser.add_argument('-host', nargs='?', default='localhost', help="The host IP for the server to listen on. Defaults to localhost.")
    parser.add_argument('-port', nargs='?', default=8000, help="The port number for the server to listen on. Defaults to 8000.")
    parser.add_argument('-method', nargs='?', default="", help="The remote method to invoke.")
    parser.add_argument('params', metavar='Message', nargs=argparse.REMAINDER, help='The parameters to the method, separated by space.')
    args = parser.parse_args()

    output = call_rpc(args.host, int(args.port), args.method, args.params)
    print (output)