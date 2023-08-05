import logging
import pkg_resources
import re
import sre_constants
import sys
import time
from django.contrib.auth.models import User
import reviewboard

def log(str):
    log = open("/var/tmp/mylog","a")
    log.write(str+"\n")
    log.close()

class HTTPAuthBackend(reviewboard.accounts.backends.AuthBackend):
    name = 'HTTPAuthBackend'
    the_url = "http://tools.projectgoth.com"
    def authenticate(self, username, password):
        import httplib
        import urllib2
        log("%s:%s" % (username, password))

        username = username.strip()

        try:
            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, self.the_url, username, password) 
            authhandler = urllib2.HTTPBasicAuthHandler(passman)
            opener = urllib2.build_opener(authhandler)
            urllib2.install_opener(opener)
            pagehandle = urllib2.urlopen(self.the_url)
            return self.get_or_create_user(username, password)
        except Exception, e:
            # FIXME I'm not sure under what situations this would fail (maybe if
            # their NIS server is down), but it'd be nice to inform the user.
            log(str(e))
            pass

        return None

    def get_or_create_user(self, username, passwd=None):
        import nis

        username = username.strip()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                first_name = username
                last_name = None

                email = u'%s@%s' % (username, 'mig33global.com')

                user = User(username=username,
                            password='',
                            first_name=first_name,
                            last_name=last_name or '',
                            email=email)
                user.is_staff = True
                user.is_superuser = False
                user.set_unusable_password()
                user.save()
            except nis.error:
                pass
        return user
