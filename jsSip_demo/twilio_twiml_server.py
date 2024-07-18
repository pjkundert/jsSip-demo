import click
import logging
import web
import os
import sys
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial


log				= logging.getLogger( 'cli' )


# Twilio configuration
account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twiml_app_sid = os.environ.get('TWILIO_TWIML_APP_SID')
sip_domain = os.environ.get('SIP_DOMAIN')

urls = (
    '/token', 'TokenGenerator',
    '/voice', 'VoiceHandler'
)


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
    sys.argv			= [sys.argv[0], interface]
    app				= web.application(urls, locals())
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
