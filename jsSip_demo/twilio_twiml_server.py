import web
import os
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial

# Twilio configuration
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twiml_app_sid = os.environ.get('TWILIO_TWIML_APP_SID')
sip_domain = os.environ.get('SIP_DOMAIN')

urls = (
    '/token', 'TokenGenerator',
    '/voice', 'VoiceHandler'
)

app = web.application(urls, globals())

class TokenGenerator:
    def GET(self):
        # Generate a random identity for this client
        identity = web.utils.random_sha1()

        # Create access token with credentials
        token = AccessToken(account_sid, auth_token, identity=identity)

        # Create a Voice grant and add to token
        voice_grant = VoiceGrant(
            outgoing_application_sid=twiml_app_sid,
            incoming_allow=True,
        )
        token.add_grant(voice_grant)

        # Return token info as JSON
        return web.json.dumps({
            'identity': identity,
            'token': token.to_jwt().decode('utf-8')
        })

class VoiceHandler:
    def POST(self):
        # Create TwiML response
        resp = VoiceResponse()
        
        # Get the 'To' parameter from the request
        to = web.input().get('To')
        
        # If 'To' is our SIP URI, approve the call
        if to == f'sip:loudspeaker@{sip_domain}':
            dial = Dial()
            dial.sip(to)
            resp.append(dial)
        else:
            resp.say("I'm sorry, but I can't connect your call at this time.")
        
        # Set response headers
        web.header('Content-Type', 'text/xml')
        return str(resp)


def main():
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit( main() )
