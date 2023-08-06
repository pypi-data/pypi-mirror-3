import pkgutil

__version__ = "0.1"

def get_script(name):
    """Get the contents of a script script from the continuous_scripts packages
    
    Example values for `name`:
        "bootstrap.sh"
        "services/mongodb"
        "continuousrc/python"
        "setupscripts/ruby"
    """
    
    return pkgutil.get_data("continuous_scripts", "scripts/%s" % name)