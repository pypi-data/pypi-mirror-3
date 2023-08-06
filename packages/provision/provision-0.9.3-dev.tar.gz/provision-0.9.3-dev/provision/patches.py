"""This module contains various monkey patches to libcloud libraries
necessary for aws support.

see: http://stackoverflow.com/questions/3765222/monkey-patch-python-class
"""

import os
import libcloud.compute.deployment

# FileDeployment can be used by all drivers, a general replacement for ex_files param

class FileDeployment(libcloud.compute.deployment.Deployment):
    """
    Install a file.
    """

    def __init__(self, source, target):
        """
        @type source: C{str}
        @keyword source: Local path of file to be installed

        @type target: C{str}
        @keyword target: Path on node to install file
        """
        self.source = source
        self.target = target

    def run(self, node, client):
        """
        Upload the file, retaining permissions

        See also L{Deployment.run}
        """
        perms = os.stat(self.source).st_mode
        client.put(path=self.target, chmod=perms,
                   contents=open(self.source, 'rb').read())
        return node

libcloud.compute.deployment.FileDeployment = FileDeployment


import libcloud.compute.types
class DeploymentError(libcloud.compute.types.LibcloudError):
    """
    Exception used when a Deployment Task failed.

    @ivar node: L{Node} on which this exception happened, you might want to call L{Node.destroy}
    """
    def __init__(self, node, original_exception=None, driver=None):
        self.node = node
        self.value = original_exception
        self.driver = driver

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (('<DeploymentError: node=%s, error=%s>'
                % (self.node.id, str(self.value))))

libcloud.compute.types.DeploymentError = DeploymentError
