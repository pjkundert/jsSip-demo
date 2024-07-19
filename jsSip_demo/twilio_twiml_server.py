import click
import json
import logging
import os
import sys
import uuid
import web

from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial


log				= logging.getLogger( 'cli' )


# Twilio configuration
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twiml_app_sid = os.environ.get('TWILIO_TWIML_APP_SID')
sip_domain = os.environ.get('SIP_DOMAIN')
twilio_from = os.environ.get('TWILIO_FROM', None)

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


@click.command()
@click.option('-i', '--interface', default="0.0.0.0:8001", help='interface:port to run the server on (default: 0.0.0.0:8001)')
def http( interface ):

    class TokenGenerator:
        def POST(self):
            log.info( f"TwiML token request: {web.input()}" )
            # Generate a random identity for this client
            identity = str( uuid.uuid4() )

            # Create access token with credentials
            token = AccessToken(
                account_sid,
                auth_token,
                twiml_app_sid,
                identity=identity
            )

            # Create a Voice grant and add to token
            voice_grant = VoiceGrant(
                outgoing_application_sid=twiml_app_sid,
                incoming_allow=True,
            )
            token.add_grant(voice_grant)

            # Return token info as JSON
            response_data = {
                'identity': identity,
                'token': token.to_jwt()
            }
            log.debug( f"Returning TwiML token: {json.dumps( response_data, indent=4 )}" )
            web.header( 'Content-Type', 'application/json' )
            return json.dumps( response_data )

    class VoiceHandler:
        def POST(self):
            log.info( f"TwiML voice request: {web.input()}" )
            # Create TwiML response
            resp = VoiceResponse()

            # Get the 'To' parameter from the request
            to = web.input().get('To') or 'sip:zifi-horn-2@eyesite.sip.twilio.com'

            # If 'To' is our SIP URI, approve the call.  For now, approves all calls
            # to anything @<sip_domain>
            #if to == f'sip:loudspeaker@{sip_domain}':
            # Just approve every request for now.
            if to.endswith( sip_domain ) or True:
                log.info( f"Dialing: {to}" )
                dial = Dial( caller_id=twilio_from )
                dial.sip( to )
                resp.append( dial )
            else:
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


cli.add_command( http )


if __name__ == "__main__":
    try:
        cli()
    except Exception as exc:
        log.exception( f"Failed due to {exc}" )
        sys.exit( 1 )
    sys.exit( 0 )
