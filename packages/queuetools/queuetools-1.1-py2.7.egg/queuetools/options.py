import optparse

def add_connection_options(parser):
    connection_group = optparse.OptionGroup(
        parser,
        "Connection options",
        "The following options define the connection to the AMQP broker."
    )
    connection_group.add_option("-H", "--host",
                                action="store",
                                default="localhost",
                                help="host or host:port of the AMQP broker (default: %default)")
    connection_group.add_option("-U", "--userid",
                                action="store",
                                default="guest",
                                help="connection username (defaut: %default)")
    connection_group.add_option("-P", "--password",
                                action="store",
                                default=None,
                                help="connection password. If blank, a password will be displayed (recommended)")
    connection_group.add_option("-V", "--vhost",
                                action="store",
                                default="/",
                                help="AMQ virtual host to connect to (default: %default)")
    parser.add_option_group(connection_group)
    