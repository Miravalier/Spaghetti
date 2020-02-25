WSS_PATH = /var/wss/spaghetti.py
SYSTEMD_PATH = /etc/systemd/system/spaghetti.wss.service

.PHONY: all

all: ${SYSTEMD_PATH} ${WSS_PATH}

${WSS_PATH}: spaghetti.py ${SYSTEMD_PATH}
	sudo cp $< $@
	sudo service spaghetti.wss restart

${SYSTEMD_PATH}: spaghetti.wss.service
	sudo cp $< $@
	sudo systemctl daemon-reload
