import pkg_resources

def datasets():
    yield ('text', pkg_resources.resource_filename(__name__, 'datasets'))
