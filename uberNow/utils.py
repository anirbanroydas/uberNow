from tornado.web import URLSpec
import base64 
import os
import time 
import datetime

from .log import Log


def unpack(first, *rest):
    return first, rest

def include(prefix, module_path):
    module = __import__(module_path, globals(), locals(), fromlist=["*"])
    urls = getattr(module, 'urls')
    print urls
    final_urls = list()
    for url in urls:
        pattern = url.regex.pattern
        if pattern.startswith("/"):
            pattern = r"%s%s" % (prefix, pattern[1:])
        else:
            pattern = r"%s%s" % (prefix, pattern)
        final_urls.append(URLSpec(pattern, url.handler_class, kwargs=url.kwargs, name=url.name))
    return final_urls
    


# random id generator
def genid(n):
    return base64.urlsafe_b64encode(os.urandom(n)).replace('=', 'e')



def epoch():
    return int(time.time())


def formLocalTime(hour, mins, meridian): 
    now = datetime.datetime.now()
    return str(now.month) + '-' + str(now.day + 1) + '-' + str(now.year) + ' ' + str(hour) + ':' + str(mins) + ':00 ' + meridian


def local2UTC(t): 
    return int(time.mktime(time.strptime(t, '%m-%d-%Y %I:%M:%S %p')))


def expires(t):
    return int(time.mktime(time.strptime(t, '%m-%d-%Y %I:%M:%S %p'))) - int(time.time())


def timeCountdown(t):
    return int(time.mktime(time.strptime(t, '%m-%d-%Y %I:%M:%S %p'))) - int(time.time())


def localTime(): 
    return str(time.strftime("%m-%d-%Y %I:%M:%S %p", time.localtime()))



def newTimeAdd(t, a):
    return (t + a)


def newTimeSub(t, s):
    return (t - s)

def timeLeft(t):
    return int(t - time.time())



# Global LOGGER Instance for the tornado instance
LOGGER = Log(app_name='ubernow.tornado') 

LOGGER.setLevel(LOGGER.INFO)


