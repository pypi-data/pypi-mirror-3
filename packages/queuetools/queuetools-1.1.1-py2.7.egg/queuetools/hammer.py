import getpass
import optparse
import functional
import sys
from queuetools.options import add_connection_options
from amqplib import client_0_8 as amqp

def hammer_options(args):
    options = optparse.OptionParser(
        prog="hammer",
        usage="%prog -X EXCHANGE [options] MESSAGE [MESSAGE2 MESSAGE3 ...]",
        description="Pumps messages into an AMQP broker."
    )
    options.add_option("-X", "--exchange",
                       action="store",
                       default="amq.fanout",
                       help="the exchange to publish on (default: %default)")
    options.add_option("-n", "--number",
                       action="store",
                       type="int",
                       default=1,
                       help="the number of times to repeat each message (default: %default)")
    options.add_option("--routing-key",
                       action="store",
                       default="",
                       metavar="KEY",
                       help="the routing key to use when sending messages (default: unset)")
    add_connection_options(options)
    return options.parse_args(args)


def main(
    args=sys.argv[1:],
    optparse=hammer_options,
    getpassword=getpass.getpass,
    connect=amqp.Connection
):
    options, messages = optparse(args)
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
            for message in messages:
                for repeat in xrange(options.number):
                    amq_message = amqp.Message(message)
                    amq_message.properties['delivery_mode'] = 2
                    chan.basic_publish(
                        amq_message,
                        exchange=options.exchange,
                        routing_key=options.routing_key
                    )
        finally:
            chan.close()
    finally:
        con.close()
