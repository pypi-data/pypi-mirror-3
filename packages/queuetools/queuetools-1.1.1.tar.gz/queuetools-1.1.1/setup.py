from setuptools import setup, find_packages

setup(
    name='queuetools',
    version='1.1.1',
    author='Owen Jacobson',
    author_email='owen.jacobson@grimoire.ca',
    
    url='http://alchemy.grimoire.ca/hg/queuetools/',
    description='A set of scripts for configuring AMQP brokers.',
    long_description="""
This package provides the following scripts, which can configure AMQP brokers
such as RabbitMQ:

* mkq - declares queues (queue.declare)
* mkx - declares exchanges (exchange.declare)
* bindq - binds queues to exchanges (queue.bind)
* unbindq - unbinds queues from exchanges (queue.unbind)
* rmq - removes queues (queue.delete)
* rmx - removes exchanges (exchange.delete)
* qcat - prints messages to stdout (channel.basic_consume)
* hammer - submits messages from the command line (channel.basic_publish)
""",
    download_url='http://alchemy.grimoire.ca/python/releases/queuetools/',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ],
    
    
    packages = find_packages(),
    
    install_requires=[
        'amqplib >= 1.0.0',
        'functional',
    ],
    
    entry_points = {
        'console_scripts': [
            'bindq = queuetools.bindq:main',
            'unbindq = queuetools.unbindq:main',
            'hammer = queuetools.hammer:main',
            'mkq = queuetools.mkq:main',
            'mkx = queuetools.mkx:main',
            'qcat = queuetools.qcat:main',
            'rmq = queuetools.rmq:main',
            'rmx = queuetools.rmx:main'
        ]
    }
)
