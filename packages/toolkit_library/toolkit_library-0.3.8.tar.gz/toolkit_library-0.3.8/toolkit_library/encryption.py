# coding=utf-8
"""
    toolkit_library.encryption
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    Generate random salt, hashcode for a password and validate the password against them.
"""
import os, hashlib


class Encryption(object):
    """All static methods, there is no need to initialize the class"""

    @staticmethod
    def generate_random_string():
        """Generate a random string, the length of the string is 64.
        The string should be ascii-only and safe to be used in an url directly.
        hexdigest() returns a string contains only [0-9a-f], so it is quite safe to use it in an url.
        """
        return hashlib.sha256(os.urandom(64)).hexdigest()

    @staticmethod
    def generate_hashcode_and_salt(password):
        """Generate a random salt, then generate hashcode for password + salt.
        returns (hashcode, salt,)
        """
        salt = Encryption.generate_random_string()
        return hashlib.sha256(password + salt).hexdigest(), salt

    @staticmethod
    def check_password(password, hashcode, salt):
        """Check if the password match the hashcode and salt"""
        return hashlib.sha256(password + salt).hexdigest() == hashcode

    @staticmethod
    def complex_enough(password, complexity):
        if password == '123456':
            return False
        return True
    # todo: create some complexity levels, from minimun to maximum. check passwords against these complexity levels
