# Security Management
__all__ = ['RightsManagement', 'CalculateDigest', 'GenerateSecretKey']

from hmac import HMAC
import random

from .architecture import *
from .storage import *

def CalculateDigest(iv, *values):
    h = HMAC(iv)
    for v in values:
        h.update(v)

    return h.hexdigest()

def GenerateSecretKey(keySize, rng = None):
    if rng is None:
        rng = random.Random()

    return ''.join(chr(rng.getrandbits(8)) for x in xrange(keySize))

class RightsManagement(Component):
    class SecurityException(Exception):
        def __init__(self, action, principal = None):
            self.action = action
            self.principal = principal
            Exception.__init__(self, '%s denied %s' % (principal or '--', action))

    class ExplicitlyDenied(SecurityException):
        pass

    def getStorage(self, role):
        return self.RightsStorage.Open(self.application, role)

    def getUserRoles(self, username):
        storage = UserStorage.Open(self.application, username)
        return storage.getUserRoles()

    def isActionPermitted(self, roles, actionName):
        if not isinstance(roles, (list, tuple)):
            roles = [roles]

        permitted = False
        for thisRole in roles:
            storage = self.getStorage(thisRole)
            try: test = storage.isActionPermitted(actionName, explicit = True)
            except self.ExplicitlyDenied:
                self.application.audit('Action %s explicitly denied for %s' % (actionName, thisRole))
                return False
            else:
                if test:
                    permitted = True

        self.application.audit('Action %s %s for %s' % (actionName, permitted and 'permitted' or 'denied', thisRole))
        return permitted

    def isUserActionPermitted(self, username, actionName):
        roles = self.getUserRoles(username)
        return self.isActionPermitted(roles, actionName)

    def checkActionPermitted(self, role, actionName):
        if self.isActionPermitted(role, actionName):
            raise self.SecurityException(actionName, role)

    def checkUserActionPermitted(self, username, actionName):
        if self.isUserActionPermitted(username, actionName):
            raise self.SecurityException(actionName, username)

    def grantAction(self, roleName, actionName):
        with self.getStorage(roleName) as access:
            if access.grant(actionName):
                self.application.audit('Permission Granted: %s for %s' % (actionName, roleName))

    def revokePermittedAction(self, roleName, actionName):
        with self.getStorage(roleName) as access:
            if access.revokeGranted(actionName):
                self.application.audit('Granted Permission Revoked: %s for %s' % (actionName, roleName))

    def revokeDeniedAction(self, roleName, actionName):
        with self.getStorage(roleName) as access:
            if access.revokeDenied(actionName):
                self.application.audit('Denied Permission Revoked: %s for %s' % (actionName, roleName))

    def denyAction(self, roleName, actionName):
        with self.getStorage(roleName) as access:
            if access.deny(actionName):
                self.application.audit('Permission Denied: %s for %s' % (actionName, roleName))

    def grantPublicAction(self, actionName):
        return self.grantAction(UserStorage.Interface.PUBLIC_ROLE, actionName)

    def getUserPrincipalName(self, username):
        return 'user-' + username
    def grantUserAction(self, username, actionName):
        return self.grantAction(self.getUserPrincipalName(username), actionName)

    def enableSuperuser(self, roleName):
        with self.getStorage(roleName) as access:
            access.enableSuperuser()

    class RightsStorage(StorageUnit):
        STORAGE_REALM = 'RightsStorage'

        class Interface(StorageUnit.Interface):
            PERMITTED_ACTIONS = 'permitted-actions'
            DENIED_ACTIONS = 'explicitly-denied-actions'

            def isAllPermitted(self):
                return self.getValue('granted-all-permissions') == 'true'
            def isNonePermitted(self):
                return self.getValue('granted-no-permissions') == 'true'

            def enableSuperuser(self):
                self.setValue('granted-all-permissions', 'true')

            def isActionExplicitlyDenied(self, actionName):
                return actionName in self.getValue(self.DENIED_ACTIONS, [])

            def isActionPermitted(self, actionName, explicit = False):
                # Superuser/Lockdown:
                if self.isNonePermitted():
                    return False
                if self.isAllPermitted():
                    return True

                if self.isActionExplicitlyDenied(actionName):
                    if explicit:
                        raise RightsManagement.ExplicitlyDenied(actionName)

                    return False

                return actionName in self.getValue(self.PERMITTED_ACTIONS, [])

            def changePermission(self, typeName, actionName, grant):
                actions = self.getValue(typeName, [])
                exists = actionName in actions

                if grant:
                    if not exists:
                        actions.append(actionName)
                elif exists:
                    actions.remove(actionName)

                self.setValue(typeName, actions)
                return True

            def grant(self, actionName):
                return self.changePermission(self.PERMITTED_ACTIONS, actionName, True)
            def deny(self, actionName):
                return self.changePermission(self.DENIED_ACTIONS, actionName, True)

            def revokeGranted(self, actionName):
                return self.changePermission(self.PERMITTED_ACTIONS, actionName, False)
            def revokeDenied(self, actionName):
                return self.changePermission(self.DENIED_ACTIONS, actionName, False)
