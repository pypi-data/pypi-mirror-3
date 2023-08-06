
__version__ = "0.1.1"

_services = None
def _load_services():
    global _services
    if _services is None:
        _services = __import__("continuous_services.services", globals(), locals(), ["*"])

def get_class_name(module, guessed_class_name):
    guessed_lower = guessed_class_name.lower()
    names = filter(lambda s: s.lower() == guessed_lower, dir(module))
    
    if not names:
        raise ValueError("Could not find class which matched the guess '%s'" % guessed_class_name)
    
    return names[0]

def get_service_class(service_name):
    _load_services()
    module = getattr(_services, service_name)
    return getattr(module, get_class_name(module, "%sService" % service_name))

def get_form_class(service_name):
    _load_services()
    module = getattr(_services, service_name)
    return getattr(module, get_class_name(module, "%sForm" % service_name))

def get_module(service_name):
    _load_services()
    return getattr(_services, service_name)

def get_modules():
    _load_services()
    modules = []
    for service_name in _services.__all__:
        module = getattr(_services, service_name)
        if not getattr(module, "DISABLED", False):
            modules.append(module)
    return modules

def get_notes(service_name):
    import os
    import os.path
    here = os.path.dirname(__file__)
    notes_file = os.path.join(here, "services", service_name, "notes.html")
    
    notes = ""
    
    if os.path.isfile(notes_file):
        with open(notes_file) as f:
            notes = "\n".join(f.readlines())
    
    return notes