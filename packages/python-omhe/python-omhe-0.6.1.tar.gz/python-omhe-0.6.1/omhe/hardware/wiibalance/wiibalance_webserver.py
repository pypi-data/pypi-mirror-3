import sys,time, cgi, BaseHTTPServer
import os, linecache

try:
    from settings import server_ip, server_port, weight_output_file
except:
    print "Sorry, I can't seem fo import the settings file."
    sys.exit(1)

servAddr=(server_ip, server_port)

class httpServHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path.find('?') != -1:
			self.path, self.query_string = self.path.split('?',1)
		else:
			self.query_string = ''
		self.send_response(200)
		self.send_header('Content-type', 'application/json')
		self.end_headers()
                f=open(weight_output_file, 'rU')
		jsonstr=f.read()
		f.close()
                #print jsonstr
		self.stout =self.wfile
		self.wfile.write(jsonstr)
                linecache.clearcache()
serv = BaseHTTPServer.HTTPServer(servAddr, httpServHandler)
print "Serving forever on http://%s:%s" % (server_ip, server_port)
print "Press Ctrl-C to kill the server"
serv.serve_forever()