import http.server
import ssl

def get_ssl_context(certfile, keyfile):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile, keyfile)
    context.set_ciphers("@SECLEVEL=1:ALL")
    return context

httpd = http.server.HTTPServer(('0.0.0.0', 4443), http.server.SimpleHTTPRequestHandler)
print( f"httpd: {httpd!r}" )
context = get_ssl_context( "cert.pem", "key.pem" )
print( f"context: {context!r}" )
httpd.socket = context.wrap_socket( httpd.socket, server_side=True )
print( f"httpd.socket: {httpd.socket!r}" )

httpd.serve_forever()
