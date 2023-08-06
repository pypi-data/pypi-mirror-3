from pyramid.view import view_config

@view_config(route_name='front.home', 
             renderer='../templates/home.genshi')
def home(request):
    return dict()
