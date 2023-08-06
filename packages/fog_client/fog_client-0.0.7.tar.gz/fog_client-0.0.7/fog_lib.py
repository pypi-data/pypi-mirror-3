import cuisine as c
import requests
import re
import sys
import subprocess
import time
import logging
logger = logging.getLogger("fog_client")

def load_conf(filename):
	import ConfigParser
	conf = ConfigParser.SafeConfigParser({"fog_host":"localhost",
									      "snapin_dir":"/tmp/"})

	obert = conf.read('/etc/fog_client.ini')

	if not obert:
		with open('/etc/fog_client.ini', 'w') as conf_file:
			conf.add_section('GENERAL')
			conf.write(conf_file)
	return conf

conf = load_conf('/etc/fog_client.ini')
FOG_HOST = conf.get("GENERAL", "fog_host")
SNAPIN_DIR = conf.get("GENERAL","snapin_dir")
FOG_OK = "#!ok"


def reboot():
	with c.mode_local():
		with c.mode_sudo():
			c.run("reboot")

def fog_request(service, args=None, fog_host=FOG_HOST):
	r = requests.get("http://%s/fog/service/%s.php" % (fog_host, service),
		             params=args)
	return r

def fog_response_dict(r):
	status = r.text.splitlines()[0]
	data_dict = {}
	if status == FOG_OK:
		data = r.text.splitlines()[1:]
		data_lower = map(lambda x:x.lower(), data)
		data_list = map(lambda x:x.split("="), data_lower)
		data_dict = dict(data_list)
	data_dict["status"] = status
	return data_dict

def get_macs():
	mac_re = "([a-fA-F0-9]{2}[:|\-]?){6}"
	mac_re_comp = re.compile(mac_re)
	with c.mode_local():
		ifconfig = c.run("ifconfig")
		macs = [mac_re_comp.search(line).group() 
		        for line in ifconfig.splitlines() 
		        if 'HW' in line]
		return macs

def get_hostname():
	with c.mode_local():
		host = c.run("hostname")
		return host

def set_hostname(host):
	with c.mode_local():
		with c.mode_sudo():
			old = get_hostname()
			c.run("hostname " + host)
			c.file_write("/etc/hostname", host)
			hosts_old = c.file_read("/etc/hosts")
			hosts_new = hosts_old.replace(old, host)
			c.file_write("/etc/hosts", hosts_new)
			logger.info("Hostname changed from %s to %s" % (old, host))

def ensure_hostname(host):
	old = get_hostname()
	if old != host:
		set_hostname(host)

def client_hostname(mac):
	params = {"mac":mac}
	r = fog_request("hostname", params)
	data = r.text.splitlines()[0]
	try:
		status, hostname = data.split('=')
		if status == FOG_OK:
			ensure_hostname(hostname)
	except ValueError:
		pass

def check_snapin(mac):
	r = fog_request("snapins.checkin", {"mac":mac})
	snapin = fog_response_dict(r)
	return snapin if snapin["status"] == FOG_OK else None

def download_snapin(mac, name, job, dirname=SNAPIN_DIR):
	r = fog_request("snapins.file",
			{"mac":mac, "taskid":job})
	with c.mode_local():
		with c.mode_sudo():
			filename = dirname + name
			with open(filename, "wb") as snapin_file:
				snapin_file.write(r.content)
				return filename

def exec_snapin(name, run_with="", args="",
	            run_with_args=""):
	with c.mode_local():
		with c.mode_sudo():
			c.file_ensure(name, mode="700")
			line = " ".join([run_with, run_with_args, name, args])
			print line
			r_code = subprocess.call(line, shell=True)
			return r_code
	#c.run()

def client_snapin(mac):
	snapin = check_snapin(mac)
	if snapin:
		jobid = snapin["jobtaskid"]
		filename = download_snapin(mac, snapin["snapinfilename"], 
			                       jobid)
		r_code = exec_snapin(name=filename, 
					run_with=snapin["snapinrunwith"],
			        args=snapin["snapinargs"],
			        run_with_args=snapin["snapinrunwithargs"])
		r = fog_request("snapins.checkin", 
			           {"mac":mac, "taskid":jobid, "exitcode":r_code})

		logger.info("Installed " + snapin["snapinfilename"] + 
			         " with returncode " + str(r_code))

		if snapin["snapinbounce"]==1:
			pass #reboot()
		if r.text==FOG_OK:
			return True
	else:
		logger.info("No snapins to install on mac " + mac)
