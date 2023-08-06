import getpass
import optparse
import sys
from queuetools.options import add_connection_options
from amqplib import client_0_8 as amqp

def mkq_options(args):
    options = optparse.OptionParser(
        prog="mkq",
        usage="%prog [options] queue1 [queue2 queue3...]",
        description="Declares queues in an AMQP broker."
    )
    options.add_option("-D", "--durable",
                       action="store_true",
                       default=False,
                       help="if set, the created queues will be declared as durable and will survive broker restarts")
    add_connection_options(options)
    return options.parse_args(args)


def main(
    args=sys.argv[1:],
    optparse=mkq_options,
    getpassword=getpass.getpass,
    connect=amqp.Connection
):
    options, queues = optparse(args)
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
            for queue in queues:
                chan.queue_declare(
                    queue=queue,
                    durable=options.durable,
                    auto_delete=False
                )
        finally:
            chan.close()
    finally:
        con.close()
