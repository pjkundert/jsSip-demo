

cert.pem:
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem


serve:		cert.pem lib/jssip.js
	./https.py


.PHONY: FORCE

lib/jssip.js: ../jsSip
	cd $< && ./node_modules/gulp/node_modules/.bin/gulp dist
	cp $</dist/jssip.js $@
