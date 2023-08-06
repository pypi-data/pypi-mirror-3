import getpass
import optparse
import sys
from queuetools.options import add_connection_options
from amqplib import client_0_8 as amqp

def mkx_options(args):
    options = optparse.OptionParser(
        prog="mkx",
        usage="%prog [options] exchange1 [exchange2 exchange3...]",
        description="Declares exchanges in an AMQP broker."
    )
    options.add_option("-D", "--durable",
                       action="store_true",
                       default=False,
                       help="if set, the created queues will be declared as durable and will survive broker restarts")
    options.add_option("-T", "--exchange-type",
                       action="store",
                       default="direct",
                       metavar="TYPE",
                       help="the exchange type to declare (default: %default)")
    add_connection_options(options)
    return options.parse_args(args)


def main(
    args=sys.argv[1:],
    optparse=mkx_options,
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
                chan.exchange_declare(
                    exchange=exchange,
                    type=options.exchange_type,
                    durable=options.durable,
                    auto_delete=False
                )
        finally:
            chan.close()
    finally:
        con.close()
