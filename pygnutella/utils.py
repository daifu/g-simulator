import socket, struct, string

# Get from: http://code.activestate.com/recipes/66517-ip-address-conversion-functions-with-the-builtin-s/
def dotted_quad_to_num(ip):
    "convert decimal dotted quad string to long integer"
    return struct.unpack('!L',socket.inet_aton(ip))[0]

def num_to_dotted_quad(n):
    "convert long int to dotted quad string"
    return socket.inet_ntoa(struct.pack('!L',n))
      
def print_hex(raw_data):
    # build translation table
    # The whole ASCII character set
    ascii = string.maketrans('','')   
    # Optional delchars argument
    nonprintable = string.translate(ascii, ascii, string.printable[:-5])
    # create filter i.e.. nonprintable -> dot  
    filter = string.maketrans(nonprintable, '.' * len(nonprintable))    
    size = len(raw_data)
    num_line = size/16 + (size%16)/(size%16)
    for i in xrange(0, num_line):
        start = i*16
        end = (i+1)*16
        for j in xrange(start, end): 
            hexstr = "  "
            if j < size:
                hexstr = "{:0<2X}".format(ord(raw_data[j]))        
            print hexstr,
        print "|", string.translate(raw_data[start:end], filter)
    return