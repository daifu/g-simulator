import socket, struct

# Get from: http://code.activestate.com/recipes/66517-ip-address-conversion-functions-with-the-builtin-s/

def dotted_quad_to_num(ip):
    "convert decimal dotted quad string to long integer"
    return struct.unpack('L',socket.inet_aton(ip))[0]

def num_to_dotted_quad(n):
    "convert long int to dotted quad string"
    return socket.inet_ntoa(struct.pack('L',n))
      
def make_mask(n):
    "return a mask of n bits as a long integer"
    return (2L<<n-1)-1

def ip_to_net_and_host(ip, maskbits):
    "returns tuple (network, host) dotted-quad addresses given IP and mask size"
    # (by Greg Jorgensen)
    n = dotted_quad_to_num(ip)
    m = make_mask(maskbits)
    host = n & m
    net = n - host
    return num_to_dotted_quad(net), num_to_dotted_quad(host)