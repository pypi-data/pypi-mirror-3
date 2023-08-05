# Example SupportExtender implementation for use with YAREST

from yarest import SupportExtender, SupportRole

class CustomExtender (SupportExtender):
    def on_pre_connect(self, logger, profile, role):
        self.profile = profile
        self.role = role
        logger.info("I ran before the SSH connection was made by the '%s'!" % (role))

    def on_session_start(self, logger, sshclient):
        logger.info("I ran when the support session started!\n")
        logger.info("I'm still the '%s', which i must cache earlier if i really need to know now or later..." % (self.role))

    def on_session_stop(self, logger, sshclient):
        logger.info("I ran when the '%s' support session stopped!\n" % (self.role))
        logger.info("The SSH server being used is '%s'\n" % (self.profile.ssh_server))
        logger.info("SSHClient.is_connected() returned '%s', so i can still use SSH functionality here..." % (sshclient.is_connected()))
