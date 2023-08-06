import fcntl,socket,struct
import ioctl_requests

def get_ip(iface):
	request = ioctl_requests.get_SIOCGIFADDR()	
	addr = socket.inet_ntoa(fcntl.ioctl(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), request, struct.pack('256s', iface[:15]))[20:24])
	return addr

def get_mask(iface):
	request = ioctl_requests.get_SIOCGIFNETMASK()
	mask = socket.inet_ntoa(fcntl.ioctl(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), request, struct.pack('256s', iface[:15]))[20:24])
	return mask

def get_broadcast(iface):
	request = ioctl_requests.get_SIOCGIFBRDADDR()
	addr = socket.inet_ntoa(fcntl.ioctl(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), request, struct.pack('256s', iface[:15]))[20:24])
	return addr