"""
    toolkit_library.string_util
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Utilities to deal with strings
"""
import re

class StringUtil(object):
    """Methods in this class are all static methods. Deal with """
    
    first_cap_re = re.compile('(.)([A-Z][a-z]+)')
    all_cap_re = re.compile('([a-z0-9])([A-Z])')
    @staticmethod
    def camelcase_to_underscore(name):
        """Convert CamelCase to camel_case"""
        temp = StringUtil.first_cap_re.sub(r'\1_\2', name)
        return StringUtil.all_cap_re.sub(r'\1_\2', temp).lower()
