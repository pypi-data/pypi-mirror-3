from silva.core.interfaces import ISilvaLocalService

class IPurgingService(ISilvaLocalService):
    """A service to store purging configurations for frontend caching
       servers"""
    
    def set_caching_servers(hosts):
        """set the frontend caching servers"""
        
    def get_caching_servers():
        """return the set of frontend caching servers"""
        
    