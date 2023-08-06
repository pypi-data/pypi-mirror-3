import getpass
import optparse
import sys
from queuetools.options import add_connection_options
from amqplib import client_0_8 as amqp

def rmx_options(args):
    options = optparse.OptionParser(
        prog="rmx",
        usage="%prog [options] exchange1 [exchange2 exchange3...]",
        description="Removes exchanges from an AMQP broker."
    )
    options.add_option("-u", "--if-unused",
                       action="store_true",
                       default=False,
                       help="if set, the exchanges will be deleted only if they're not in use")
    add_connection_options(options)
    return options.parse_args(args)


def main(
    args=sys.argv[1:],
    optparse=rmx_options,
    getpassword=getpass.getpass,
    connect=amqp.Connection
):
    options, exchanges = optparse(args)
    if options.password is None:
        options.password = getpassword()

    con = connect(
        host=options.host,
        userid=options.userid,
        password=options.password,
        virtual_host=options.vhost
    )
    try:
        chan = con.channel()
        try:
            for exchange in exchanges:
                chan.exchange_delete(
                    exchange=exchange,
                    if_unused=options.if_unused
                )
        finally:
            chan.close()
    finally:
        con.close()
