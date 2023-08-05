"""
    toolkit_library
    ~~~~~~~~~~~~~~~
    General purpose toolkit library
    In order to use this library, your have to do either of the following:
    1). Install the library. (recommended)
        python setup.py install

    2). Add this library to environment variable PYTHONPATH
        export PYTHONPATH=/path/to/toolkit/library
        You can check the variable: echo $PYTHONPATH

    3). In your app, adds this library to sys.path:
        import sys
        path = '/path/to/toolkit/library'
        if path not in sys.path:
            sys.path.append(path)

    4). Copy and Paste the code to your app. This is very bad practice. Do this unless you have no other choices.


    How to use the library:
        from toolkit_library.mail_server import MailServer
        # do something with MailServer

    For more working examples, please refer to tests.py
"""
