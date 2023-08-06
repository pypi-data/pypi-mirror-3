import os, os.path, tempfile, shutil

from Base import Transport as BaseTransport
import logging
LOG = logging.getLogger('Broker.Transport.DropBox')

class Transport(BaseTransport):
    """
    Abstracts access to a broker server using file system.
    """

    def __init__(self, directory, good=".good", tmp="_py", prefix='brk_'):
        """
        Constructs a client object to send messages to a broker using the file system.
        good is the extension messages should have to signal they should be sent.
        tmp is the extension messages have while they are being written to disk.
        """
        BaseTransport.__init__(self)

        if good == tmp:
            raise ValueError ("good and tmp must be different (%r == %r)" % good, tmp)
        else:
            self.__directory = directory
            self.__good      = good
            self.__tmp       = tmp
            self.__prefix    = prefix

            if os.path.isdir( directory ):
                LOG.debug("directory %r already exists.")
            else:
                LOG.info("directory %r doesn't exist. Creating it")
                #What should the access mode be?
                os.makedirs(directory) 

    def send(self, message):
        LOG.info("send(%r)", message)

        #create temporary file
        (tmpfd, tmpname) = tempfile.mkstemp(prefix=self.__prefix, suffix=self.__tmp, dir=self.__directory)
        tmpfile = os.fdopen(tmpfd, 'w')
        tmpfile.write(message.payload)
        tmpfile.close()

        #move to destination
        destname = tmpname + self.__good
        shutil.move(tmpname, destname)

        return self
    
    def receive(self):
        raise NotImplementedError("DropBox can't receive messages")
        #dropbox doesn't/can't implement receive
