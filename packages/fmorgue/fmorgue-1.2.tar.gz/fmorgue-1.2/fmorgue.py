#!/usr/bin/env python

import os,sys,xmlrpclib,logging,socket,argparse,time,ConfigParser
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler, CGIXMLRPCRequestHandler

PROTOCOL_VERSION=1
serverconfig='/etc/fmorgue'

class Server:
	logpath=""
	withorigname=False
	withhostname=False

	# server function to check if file was already transmitted
	def checkFingerprints(self, host, clientprints):
		logging.debug("Got %u fingerprints from %s"%(len(clientprints),host))
		totransmit=[]
		logging.debug("Checking local directory "+self.logpath)
		fullpaths=[self.logpath+fname for fname in os.listdir(self.logpath)]
		localprints=get_fngprints(fullpaths).values()
		for size, mtime in clientprints:
			for localsize, localmtime in localprints:
				if localsize==size and localmtime==mtime:
					logging.debug('[%s, %s] exists already'%(str(localsize), str(localmtime)) )
					break
			else:
				totransmit.append([size, mtime])	
				logging.debug('[%s, %s] needs transfer'%(str(size), str(mtime)) )
		return totransmit
	
	#server function for letting the clients check the version of the 'protocol'
	def checkVersion(self):
		logging.debug("Got checkVersion request")
		return PROTOCOL_VERSION

	def uploadFile(self, clienthost, origname, fngprint, binary):
		logging.debug("Got data for fingerprint %s"%(str(fngprint)))
		mtime=fngprint[1]
		if self.withhostname:
			prefix=clienthost+"-"
		else:
			prefix=""		
		if ".." in origname:
			origname="contained_double_dot"
		if self.withorigname:
			#TODO: This implies that source and destination host have the same os.sep
			suffix="-"+origname[origname.rfind(os.sep)+1:]
		else:
			dotpos=origname.find('.')
			if dotpos==-1:
				suffix=""
			else:
				suffix=origname[dotpos:]
		# we generate the time string part with local time, so that it matches to
		# the printed mtime from ls -l
		timestr=time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(mtime))
		if self.logpath[-1]!=os.sep:
			self.logpath+=os.sep
		fname=self.logpath+prefix+timestr+suffix		
		logging.debug("Writing "+fname)
		# write data
		f=open(fname,"wb")
		f.write(binary.data)
		f.close()
		# change local mtime according to the fingerprint so that the later match works
		stat=os.stat(fname)
		os.utime(fname, (stat.st_atime, mtime))
		# check if the mtime is correct now
		stat=os.stat(fname)
		if stat.st_mtime != mtime:
			print("Fatal error: Setting of local mtime is not accurate.")
			exit(-1)
		return True

def get_fngprints(filepaths):
	fngprints={}
	for fname in filepaths:
		if os.path.isfile(fname):
			try:
				stat=os.stat(fname)
				fngprints[fname]=[stat.st_size, stat.st_mtime]
				logging.debug("Found "+fname+":"+str(fngprints[fname]))
			except Exception, e:
				logging.warning("Ignoring %s, file is not accessible: %s"%(fname, str(e)))
	return fngprints

def runserver():
	srv=Server()
	# logging.basicConfig(filename='/tmp/fmorgue.log',level=logging.DEBUG)
	config=ConfigParser.ConfigParser()
	try:
		config.read(serverconfig)
		srv.logpath=config.get('fmorgue-server','dir')
		srv.withhostname=config.get('fmorgue-server','withhostname')
		srv.withorigname=config.get('fmorgue-server','withorigname')
	except Exception,e:
		logging.error("Error while parsing config file "+serverconfig+": "+str(e))
		exit(-1)
	if 'REQUEST_METHOD' in os.environ:
		# run as CGI server
		cgiserver = CGIXMLRPCRequestHandler()
		cgiserver.register_instance(srv)
		cgiserver.handle_request()
	else:
		# run as standalone server
		parser = argparse.ArgumentParser(description='FMORGUE server for archiving files that will never change again, such as log-rotated files. Runs automatically in CGI or local server mode. Stored files are named according to their last modification time.')
		parser.add_argument('--port', nargs=1, type=int, metavar='number', help='The port number of the server. Ignored in CGI mode. Default value is 8000.')
		parser.add_argument('--withhostname', default=False, action='store_true', help='Add the originating host name to the archive file name.')
		parser.add_argument('--withorigname', default=False, action='store_true', help='Add the client-side original file name to the archive file name.')
		parser.add_argument('dir', help='The directory used for storage.')
		args = parser.parse_args()		
		if args.port:
			port=args.port
		else:
			port=[8000]
		# overload config file settings with command line arguments
		if args.withorigname:
			srv.withorigname=True
		if args.withhostname:
			srv.withhostname=True
		srv.logpath=args.dir
		server = SimpleXMLRPCServer( ('localhost',int(port[0])) )
		server.register_instance(srv)
		server.serve_forever()

def runclient():
	parser = argparse.ArgumentParser(description='Archive files to a remote FMORGUE server, regardless of their filename.')
	parser.add_argument('server', help='The server URL, e.g. http://example.com:8001/fmorgue-server')
	parser.add_argument('file', nargs='+', help='File to be transmitted. Only files with unknown (mtime,size) fingerprint are transmitted to the server.')
	args = parser.parse_args()
	fngprints=get_fngprints(args.file)
	logging.debug("Connecting to "+args.server)
	hstname=socket.gethostname()
	s=xmlrpclib.ServerProxy(args.server)
	try:
		version=s.checkVersion()
		if version != PROTOCOL_VERSION:
			print("Server version is %u, client version is %u. Please update your server."%(version, PROTOCOL_VERSION))
			exit(-1)
		totransmit=s.checkFingerprints(hstname, fngprints.values())	
	except Exception, e:
		logging.error("Server call failed: "+str(e))
		exit(-1)
	logging.debug("%u files to transmit"%(len(totransmit)))
	for fname, fngprint in fngprints.iteritems():
		if fngprint in totransmit:
			logging.debug("Sending "+fname)
			s.uploadFile(hstname, fname, fngprint, xmlrpclib.Binary(open(fname, "rb").read()))
