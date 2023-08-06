#!/usr/bin/env python
import logging
import logging.handlers
import time
import itertools as it
from fog_lib import get_macs, client_hostname, client_snapin, load_conf

def main():
	macs = get_macs()
	logger.info("Service started")
	for mac in macs:
		logger.info("Detected mac: " + mac)
	while True:
		time.sleep(5)
		for mac in macs:
			client_hostname(mac)
			client_snapin(mac, FOG_HOST, SNAPIN_DIR)

if __name__ == '__main__':
	requests_log = logging.getLogger("requests")
	requests_log.setLevel(logging.WARNING)
	logger = logging.getLogger("fog_client")
	logger.setLevel(logging.INFO)
	handler = logging.handlers.RotatingFileHandler('/var/log/fog.log',
                                               maxBytes=8192,
                                               backupCount=5,
                                               mode='w')
	formatter = logging.Formatter(fmt='%(levelname)s:%(asctime)s:%(message)s',
					          datefmt='%d/%m/%Y-%I:%M:%S')
	handler.setFormatter(formatter)
	logger.addHandler(handler)

	conf = load_conf('/etc/fog_client.ini')
	fog_host = conf.get("GENERAL", "fog_host")
	snapin_dir = conf.get("GENERAL","snapin_dir")
	main()
