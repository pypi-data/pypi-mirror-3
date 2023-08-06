import getpass
import optparse
import sys
from queuetools.options import add_connection_options
from amqplib import client_0_8 as amqp

def bindq_options(args):
    options = optparse.OptionParser(
        prog="bindq",
        usage="%prog [options] queue exchange",
        description="Binds a queue to an exchange in an AMQP broker."
    )
    options.add_option("--routing-key",
                       action="store",
                       default="",
                       metavar="KEY",
                       help="the routing key to use when binding the queue from its exchange (default: unset)")
    add_connection_options(options)
    return options.parse_args(args)


def main(
    args=sys.argv[1:],
    optparse=bindq_options,
    getpassword=getpass.getpass,
    connect=amqp.Connection
):
    options, (queue, exchange) = optparse(args)
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
            chan.queue_bind(
                queue=queue,
                exchange=exchange,
                routing_key=options.routing_key
            )
        finally:
            chan.close()
    finally:
        con.close()
