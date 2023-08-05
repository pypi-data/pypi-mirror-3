from setuptools import setup

version = '20110917'
name = 'minimumTFTP'
short_description = 'tftp server and client.'
long_description = """\
tftp server and client.

Requirements
------------
* Python 3.x


usage:
    >>> import minimumTFTP

    ## server running
    >>> tftpServer = minimumTFTP.Server('C:\\server_TFTP_Directory')
    >>> tftpServer.run()

    ## client running
    ##  arg1: server_IP_address
    ##  arg2: client_directory
    ##  arg3: get or put filename
    >>> tftpClient = minimumTFTP.Client(arg1, arg2, arg3)

    ## get
    >>> tftpClient.get()

    ## put
    >>> tftpClient.put()


python -m
    server runnning
        Usage: python -m minimumTFTP -s [directory]

    client get
        Usage: python -m minimumTFTP -g [serverIP] [directory] [filename]

    client put
        Usage: python -m minimumTFTP -p [serverIP] [directory] [filename]
"""

classifiers = [
   "Development Status :: 3 - Alpha",
   "License :: OSI Approved :: BSD License",
   "Programming Language :: Python :: 3",
   "Topic :: Internet",
   "Environment :: Console",
]

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    keywords=['network','internet','tftp',],
    author='shigekiyamada',
    author_email='yam@tokyo.email.ne.jp',
    url='',
    license='BSD',
)