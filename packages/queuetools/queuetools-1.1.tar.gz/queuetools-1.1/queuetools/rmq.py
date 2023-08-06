import getpass
import optparse
import sys
from queuetools.options import add_connection_options
from amqplib import client_0_8 as amqp

def rmq_options(args):
    options = optparse.OptionParser(
        prog="rmq",
        usage="%prog [options] queue1 [queue2 queue3...]",
        description="Removes queues from an AMQP broker."
    )
    options.add_option("-u", "--if-unused",
                       action="store_true",
                       default=False,
                       help="if set, the queues will be deleted only if they're not in use")
    options.add_option("-e", "--if-empty",
                       action="store_true",
                       default=False,
                       help="if set, the queues will be deleted only if they hold no undelivered messages")
    add_connection_options(options)
    return options.parse_args(args)


def main(
    args=sys.argv[1:],
    optparse=rmq_options,
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
                chan.queue_delete(
                    queue=queue,
                    if_empty=options.if_empty,
                    if_unused=options.if_unused
                )
        finally:
            chan.close()
    finally:
        con.close()
