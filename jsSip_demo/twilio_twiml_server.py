import click
import json
import logging
import os
import re
import sys
import uuid
import web

from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial


log				= logging.getLogger( 'cli' )


# Twilio configuration
twilio_number			= os.environ.get('TWILIO_CALLER_ID')
account_sid			= os.environ.get('TWILIO_ACCOUNT_SID')
auth_token			= os.environ.get('TWILIO_AUTH_TOKEN')
twiml_app_sid			= os.environ.get('TWILIO_TWIML_APP_SID')
api_key				= os.environ.get('API_KEY')
api_secret			= os.environ.get('API_SECRET')
sip_domain			= os.environ.get('SIP_DOMAIN')

client_default			= 'sip:zifi-horn-2@eyesite.sip.twilio.com'


log_cfg                         = {
    "level":    logging.WARNING,
    "datefmt":  '%Y-%m-%d %H:%M:%S',
    "format":   '%(asctime)s %(name)-16.16s %(message)s',
}


log_levelmap                    = {
    -2: logging.FATAL,
    -1: logging.ERROR,
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG,
}


def log_level( adjust ):
    """Return a logging level corresponding to the +'ve/-'ve adjustment"""
    return log_levelmap[
        max(
            min(
                adjust,
                max( log_levelmap.keys() )
            ),
            min( log_levelmap.keys() )
        )
    ]


@click.group()
@click.option('-v', '--verbose', count=True)
@click.option('-q', '--quiet', count=True)
def cli( verbose, quiet ):
    cli.verbosity               = verbose - quiet
    log_cfg['level']            = log_level( cli.verbosity )
    logging.basicConfig( **log_cfg )
    if verbose or quiet:
        logging.getLogger().setLevel( log_cfg['level'] )
cli.verbosity                   = 0  # noqa: E305


alphanumeric_only		= re.compile( r"[\W_]+" )
phone_pattern			= re.compile( r"^[\d\+\-\(\) ]+$" )
sip_uri				= re.compile( r"^\s*sip:.*$" )

@click.command()
@click.option('-i', '--interface', default="0.0.0.0:8001", help='interface:port to run the server on (default: 0.0.0.0:8001)')
def http( interface ):

    class TokenGenerator:
        def POST(self):
            log.info( f"TwiML token request: {web.input()}" )
            # Generate a random identity for this client, and remember the latest one for routing
            identity = str( uuid.uuid4() )
            http.IDENTITY["identity"] = identity
            log.debug( f"AccessToken SID: {account_sid[:4]}..., API {api_key[:4]}.../{api_secret[:4]}..., ID: {identity[:4]}..." )
            # Create access token with credentials
            token = AccessToken(
                account_sid,
                api_key,
                api_secret,
                identity=identity
            )

            # Create a Voice grant and add to token
            log.debug( f"VoiceGrant APP SID: {twiml_app_sid[:4]}..." )
            voice_grant = VoiceGrant(
                outgoing_application_sid=twiml_app_sid,
                incoming_allow=True,
            )
            token.add_grant(voice_grant)

            # Return token info as JSON
            response_data = {
                'identity': identity,
                'token': token.to_jwt(),
            }
            log.debug( f"Returning TwiML token: {json.dumps( response_data, indent=4 )}" )
            web.header( 'Content-Type', 'application/json' )
            return json.dumps( response_data )

    class VoiceHandler:
        def POST(self):
            log.info( f"TwiML voice request: {web.input()}" )

            # Create TwiML response
            resp		= VoiceResponse()

            # Get the 'To' parameter from the request
            to			= web.input().get('To') # or 

            if to == twilio_number:
                # Receive an inbound call to our Twilio number:
                dest		= http.IDENTITY.get( "identity", client_default )
                log.info( f"Incoming call: {to} ==> {dest}" )
                dial.client( dest )  # Handle +###..., sip:..., ...?
                resp.append( dial )
            elif to:
                # Place an outbound call
                # conf = Dial( caller_id=twilio_number )
                # conf.conference(
                #     f"EyeSite Paging {to}",
                #     wait_url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.classical"
                # )
                # resp.append( conf )
                # Now add this caller to the conference
                dial = Dial( caller_id=twilio_number )
                if phone_pattern.match( to ):
                    log.info( f"Outgoing call (PSTN): {to}" )
                    dial.number( to )
                elif sip_uri.match( to ):
                    log.info( f"Outgoing call (SIP):  {to}" )
                    dial.sip( to )
                else:
                    log.info( f"Outgoing call (???):  {to}" )
                    dial.client( to )
                resp.append( dial )
                resp.say( "Hello" )
                resp.play("https://pbx.admin.zifi.ca/static/sound/pump-action.mp3")
            else:
                log.info( f"Can't connect: {to}" )
                resp.say("I'm sorry, but I can't connect your call at this time.")

            # Set response headers
            web.header('Content-Type', 'text/xml')
            resp_xml = str( resp )
            log.debug( f"TwiML response: {resp_xml}"  )
            return resp_xml

    urls			= (
        '/token', 'TokenGenerator',
        '/voice', 'VoiceHandler'
    )

    sys.argv			= [sys.argv[0], interface]
    app				= web.application( urls, locals() )
    app.run()
    return 0

# Store the most recently created identity in memory for routing calls
http.IDENTITY = {"identity": ""}


cli.add_command( http )


if __name__ == "__main__":
    try:
        cli()
    except Exception as exc:
        log.exception( f"Failed due to {exc}" )
        sys.exit( 1 )
    sys.exit( 0 )
