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
    
    @reify
    def user_id(self):
        """Current logged in user object
        
        """
        from pyramid.security import authenticated_userid
        user_id = authenticated_userid(self)
        return user_id
    
    @reify
    def user(self):
        """Current logged in user
        
        """
        from .models.user import UserModel
        if self.user_id is None:
            return None
        model = UserModel(self.read_session)
        user = model.get_user_by_id(self.user_id)
        return user
    
    def add_flash(self, *args, **kwargs):
        from .flash import add_flash
        return add_flash(self, *args, **kwargs)
    