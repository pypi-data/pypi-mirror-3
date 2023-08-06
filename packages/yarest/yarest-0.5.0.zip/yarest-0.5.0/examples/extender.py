# Example SupportExtender implementation for use with YAREST

from yarest import SupportExtender

class CustomExtender (SupportExtender):
    def on_pre_connect(self, entity):
        entity.logger.info("I ran directly before the SSH connection was made to server '%s'!" % (entity.profile.ssh_server))

    def on_session_start(self, entity):
        entity.logger.info("I ran directly after the support session started!")
        entity.logger.info("The remote server port number in use is '%d'." % (entity.remoteport))
        entity.logger.info("The SSH tunnel direction in use is '%s'." % (entity.profile.support_tunnel))

    def on_session_stop(self, entity):
        entity.logger.info("I ran directly after the support session stopped!")
        entity.logger.info("The SSH server being used is still '%s'" % (entity.profile.ssh_server))
        entity.logger.info("'SSHClient.is_connected()' returned '%s', so i can still use SSH functionality here..." % (entity.sshclient.is_connected()))
