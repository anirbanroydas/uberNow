from tornado import gen
import pymongo.errors
import random

import uberNow.utils

LOGGER = uberNow.utils.LOGGER

MAX_AUTO_RECONNECT_ATTEMPTS = 20 
MAX_DUPLICATE_ERROR_ATTEMPTS = 20
MAX_EXECUTIONS_LIMIT = 5
MAX_RECONNECTIONS_LIMIT = 5


def handle_failover(f):
	@gen.coroutine
	def wrapper(*args, **kwargs):
		retries = MAX_AUTO_RECONNECT_ATTEMPTS
		duplicates = MAX_DUPLICATE_ERROR_ATTEMPTS
		executions = MAX_EXECUTIONS_LIMIT
		reconnections = MAX_RECONNECTIONS_LIMIT 
		t = 1
		i = 0
		j = 0
		k = 0
		l = 0
		while True:
			try:
				ret = yield f(*args, **kwargs)
				raise gen.Return(ret)
			except pymongo.errors.AutoReconnect, e:
				if i < retries:
					t = random.uniform(0.35, 0.55) ** (retries - i)
					i = i + 1
					yield gen.sleep(t)
				else:
					# Log the Autoreconnect error since its unable to reconnect
					LOGGER.error({'location': 'uberNow.apps.apicalls.mongodb_api.handle_failover.wrapper',
                                            'msg': 'pymongo.errors.AutoReconnec',
                                            'description': str(e) + ' for websocket obj = [%s]' % str(kwargs['new_id'])
                   })
					raise gen.Return(-1)

			except pymongo.errors.DuplicateKeyError, e:
				if j < duplicates:
					j = j + 1
					kwargs['new_id'] = uberNow.utils.genid(32)
				else:
					# Log the Duplicate error
					LOGGER.error({'location': 'uberNow.apps.apicalls.mongodb_api.handle_failover.wrapper',
	                                    'msg': 'pymongo.errors.DuplicateKeyError',
	                                    'description': str(e) + ' for websocket obj = [%s]' % str(kwargs['new_id'])
	                  })
					raise gen.Return(-2)
			except pymongo.errors.ExecutionTimeout, e:
				if k < executions:
					t = random.uniform(0.35, 0.55) ** (executions - k)
					k = k + 1
					yield gen.sleep(t)
				else:
					# Log the ExecutionTimeout error
					LOGGER.error({'location': 'uberNow.apps.apicalls.mongodb_api.handle_failover.wrapper',
	                                    'msg': 'pymongo.errors.ExecutionTimeout',
	                                    'description': str(e) + ' for websocket obj = [%s]' % str(kwargs['new_id'])
	                  })
					raise gen.Return(-3)

			except pymongo.errors.NetworkTimeout, e:
				if l < reconnections:
					t = random.uniform(0.35, 0.55) ** (reconnections - l)
					l = l + 1
					yield gen.sleep(t)
				else:
					# Log the NetworkTimeout error
					LOGGER.error({'location': 'uberNow.apps.apicalls.mongodb_api.handle_failover.wrapper',
	                                    'msg': 'pymongo.errors.NetworkTimeout',
	                                    'description': str(e) + ' for websocket obj = [%s]' % str(kwargs['new_id'])
	                  })
					raise gen.Return(-4)

			except Exception, e:
				# Log other Exceptions
				LOGGER.error({'location': 'uberNow.apps.apicalls.mongodb_api.handle_failover.wrapper',
                                    'msg': str(e.__class__.__name__),
                                    'description': str(e) + ' for websocket obj = [%s]' % str(kwargs['new_id'])
                  })
				raise gen.Return(-5)

				
				

	yield wrapper
