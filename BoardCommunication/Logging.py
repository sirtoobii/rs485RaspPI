import logging
class Log:
    def __init__(self, xapp, logname="rs485"):
        class O:
            def __init__(self, xapp, logname="rs485"):
                self.logger = logging.getLogger(logname)

            def write(self, s):
                self.logger.debug(s)

        self.app = xapp
        self.f = O(logname)

    def __call__(self, environ, start_response):
        environ['rs485.errors'] = self.f
        return self.app(environ, start_response)
