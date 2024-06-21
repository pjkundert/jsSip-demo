

cert.pem:
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem


serve:		cert.pem lib/jsSIP/jssip.js



.PHONY: FORCE

lib/jsSIP/jssip.js: ../jsSip FORCE
	cd $< && ./node_modules/gulp/node_modules/.bin/gulp dist
	cp $</dist/jssip.js $@
