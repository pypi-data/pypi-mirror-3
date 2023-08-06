import getpass
import optparse
import functional
import sys
from queuetools.options import add_connection_options
from amqplib import client_0_8 as amqp

def echo(chan, msg):
    print str(msg.body)
    chan.basic_ack(msg.delivery_tag)

def qcat_options(args):
    options = optparse.OptionParser(
        prog="qcat",
        usage="%prog -Q QUEUE [options]",
        description="Consumes and displays messages from an AMQP queue."
    )
    options.add_option("-Q", "--queue",
                       action="store",
                       help="the queue to consume from")
    options.add_option("--drain",
                       action="store_true",
                       default=False,
                       help="if set, the consume transaction will be committed at exit, removing all displayed messages from the queue permanently. Otherwise, the transaction will be rolled back at exit, allowing messages to be redelivered.")
    add_connection_options(options)
    queue_config_group = optparse.OptionGroup(
        options,
        "Broker setup options",
        "The following options allow qcat to create and bind queues. If none of them are set, qcat can only operate on pre-existing queues."
    )
    queue_config_group.add_option("--declare-queue",
                                  action="store_true",
                                  default=False,
                                  help="ensures QUEUE exists by declaring it before consuming messages")
    queue_config_group.add_option("--declare-exchange",
                                  action="store_true",
                                  default=False,
                                  help="ensures EXCHANGE exists as a TYPE exchange by declaring it before consuming messages")
    queue_config_group.add_option("--bind-queue",
                                  action="store_true",
                                  default=False,
                                  help="ensures QUEUE is bound to EXCHANGE using KEY before consuming messages")
    queue_config_group.add_option("-X", "--exchange",
                                  action="store",
                                  default="amq.direct",
                                  help="the exchange to declare or bind against (default: %default)")
    queue_config_group.add_option("-T", "--exchange-type",
                                  action="store",
                                  default="direct",
                                  metavar="TYPE",
                                  help="the exchange type to declare (default: %default)")
    queue_config_group.add_option("-D", "--durable",
                                  action="store_true",
                                  default=False,
                                  help="if set, queues and exchanges will be declared as durable")
    queue_config_group.add_option("-A", "--auto-delete",
                                  action="store_true",
                                  default=False,
                                  help="if set, queues and exchanges will be declared as auto-deleteable")
    queue_config_group.add_option("--routing-key",
                                  action="store",
                                  default="",
                                  metavar="KEY",
                                  help="the routing key to use when binding the queue to its exchange (default: unset)")
    options.add_option_group(queue_config_group)
    return options.parse_args(args)


def main(
    args=sys.argv[1:],
    optparse=qcat_options,
    getpassword=getpass.getpass,
    connect=amqp.Connection
):
    options, args = optparse(args)
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
            if options.declare_queue:
                chan.queue_declare(
                    queue=options.queue,
                    durable=options.durable,
                    auto_delete=options.auto_delete
                )
            if options.declare_exchange:
                chan.exchange_declare(
                    exchange=options.exchange,
                    type=options.exchange_type,
                    durable=options.durable,
                    auto_delete=options.auto_delete
                )
            if options.bind_queue:
                chan.queue_bind(
                    queue=options.queue,
                    exchange=options.exchange,
                    routing_key=options.routing_key
                )
            
            chan.tx_select()
            consumer_tag = chan.basic_consume(
                callback=functional.partial(echo, chan),
                queue=options.queue
            )
            try:
                print "Press ^C to exit..."
                while True:
                    chan.wait()
            except KeyboardInterrupt:
                print # A newline, so that ^C doesn't naff up readline.
            finally:
                chan.basic_cancel(consumer_tag)
                if options.drain:
                    chan.tx_commit()
                else:
                    chan.tx_rollback()
        finally:
            chan.close()
    finally:
        con.close()
