def map_front(config):
    # front pages
    config.add_route('front.home', '/')
    
def map_static_files(config):
    config.add_static_view('static', 'static', 
                           cache_max_age=8640000) # 100 days
    config.add_route('static_files.favicon', '/favico.ico')
    
def map_urls(config):
    config.include(map_static_files)
    config.include(map_front)