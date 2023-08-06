#!/usr/bin/env python
import logging
import logging.handlers
import time
from fog_lib import get_macs, client_hostname, client_snapin

def main():
	macs = get_macs()
	logger.info("Service started")
	for mac in macs:
		logger.info("Detected mac: " + mac)
	while True:
		time.sleep(60)
		map(client_hostname, macs)
		map(client_snapin, macs)

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

	main()
