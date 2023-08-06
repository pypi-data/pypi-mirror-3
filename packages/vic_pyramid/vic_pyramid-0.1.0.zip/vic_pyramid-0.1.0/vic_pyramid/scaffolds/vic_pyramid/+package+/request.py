from pyramid.request import Request
from pyramid.decorator import reify

class WebRequest(Request):
    
    @reify
    def read_session_maker(self):
        """Read-only session maker
        
        """
        settions = self.registry.settings
        return settions['read_session_maker']
    
    @reify
    def read_session(self):
        """Read-only session, optimized for read
        
        """
        return self.read_session_maker()
    
    @reify
    def write_session_maker(self):
        """Read/Write session, use this session only for updating database
        
        """
        settions = self.registry.settings
        return settions['write_session_maker']
    
    @reify
    def write_session(self):
        """Read-only session, optimized for read
        
        """
        return self.write_session_maker()