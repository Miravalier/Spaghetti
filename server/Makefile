# Configuration
APP_NAME := spaghetti
APP_TYPE := api

# Constant Variables
APP_PATH := /var/${APP_TYPE}/${APP_NAME}.py
SYSTEMD_PATH := /etc/systemd/system/${APP_NAME}.${APP_TYPE}.service


${APP_PATH}: ${APP_NAME}.py ${SYSTEMD_PATH}
	sudo cp $< $@
	sudo service ${APP_NAME}.${APP_TYPE} restart

${SYSTEMD_PATH}: ${APP_NAME}.${APP_TYPE}.service
	sudo cp $< $@
	sudo systemctl daemon-reload

install: ${SYSTEMD_PATH} ${APP_PATH}

uninstall:
	sudo service ${APP_NAME}.${APP_TYPE} stop
	sudo rm -f ${APP_PATH} ${SYSTEMD_PATH}
	sudo systemctl daemon-reload

.PHONY: install uninstall
