# from metlog.client import MetlogClient
# from metlog.config import client_from_dict_config


# class MetlogClientWrapper(object):
#     """
#     This class acts as a lazy proxy of sorts to the MetlogClient. We need this
#     to provide late binding of the MetlogClient so that decorators which use
#     Metlog have a chance to be configured prior to affecting the callable which
#     is being decorated.
#     """
#     def __init__(self):
#         self.reset()

#     def activate(self, client_config):
#         """
#         Applies configuration to the wrapped client, allowing it to be used and
#         activating any Metlog decorators that might be in use.

#         :param client_config: Dictionary containing MetlogClient configuration.
#         """
#         client_from_dict_config(client_config, client=self.client)
#         disabled_decorators = [k.replace("disable_", '')
#                                for (k, v) in client_config.items()
#                                if (k.startswith('disable_') and v)]
#         self._disabled_decorators = set(disabled_decorators)
#         self.is_activated = True

#     def reset(self):
#         """
#         Sets client related instance variables to default settings.
#         """
#         self.client = MetlogClient()
#         self._disabled_decorators = set()
#         self.is_activated = False

#     def decorator_is_disabled(self, name):
#         # Check if this particular logger is disabled
#         return name in self._disabled_decorators

# CLIENT_WRAPPER = MetlogClientWrapper()


# def getLogger(name='root'):
#     pass
