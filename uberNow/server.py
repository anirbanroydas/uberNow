import tornado.ioloop
import tornado.httpserver
import tornado.web
from tornado.options import define, options
# import logging
import motor.motor_tornado
import redis
import uuid
from pytz import utc
from apscheduler.schedulers.tornado import TornadoScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.executors.gevent import GeventExecutor

from urls import urls
from settings import settings
import utils


define("port", default=9091, help="run on the given port", type=int)
define("model", default='buest_guess',
       help="the traffic_model to use to poll google maps apis, like buest_guess or pessimistic", type=str)
define("with_celery", default=False, help="run using celery workers", type=bool)
# define("with_rabbitmq_pubsub", default=False, help="run without celery but with rabbitmq for pub sub", type=bool)

# LOGGER = logging.getLogger(__name__)
LOGGER = utils.LOGGER


PROCESS_ID = uuid.uuid4()

JOBSTORES = {
    'default': RedisJobStore(jobs_key='uberNow.jobs:' + PROCESS_ID,
                             run_times_key='uberNow.run_times:' + PROCESS_ID,
                             unix_socket_path='/usr/loca/var/run/redis/redis.sock')
}

EXECUTORS = {
    'default': GeventExecutor()
}

JOB_DEFAULTS = {
    'coalesce': False,
    'max_instances': 3
}



class Application(tornado.web.Application):

    def __init__(self, with_celery, model):
        tornado.web.Application.__init__(self, urls, **settings)
        self.mongo_client = motor.motor_tornado.MotorClient(
            '/usr/local/var/run/mongodb/mongodb-27017.sock')
        self.db = self.mongo_client.ubernow
        self.redis = redis.StrictRedis(unix_socket_path='/usr/loca/var/run/redis/redis.sock')
        self.scheduler = TornadoScheduler(
            jobstores=JOBSTORES, executors=EXECUTORS, job_defaults=JOB_DEFAULTS, timezone=utc)
        self.scheduler.start()
        self.model = model
        self.with_celery = with_celery
        # self.with_rabbitmq_pubsub = with_rabbitmq_pubsub


def main():
    tornado.options.parse_command_line()
    app = Application(options.with_celery, options.model)
    http_server = tornado.httpserver.HTTPServer(app, no_keep_alive=True)
    http_server.listen(options.port)

    LOGGER.info('[server.main] Starting server on http://127.0.0.1:%s', options.port)


    try:
        LOGGER.info("\n[server.main] Server Started.\n")

        tornado.ioloop.IOLoop.current().start()

    except KeyboardInterrupt:
        LOGGER.error('\n[server.main] EXCEPTION KEYBOARDINTERRUPT INITIATED\n')
        LOGGER.info("[server.main] Stopping Server....")
        LOGGER.info(
            '[server.main] closing all websocket connections objects and corresponsding mqtt client objects')
        LOGGER.info('Stopping Tornado\'s main iolooop')

        # Stopping main thread's ioloop, not to be confused with current thread's ioloop
        # which is ioloop.IOLoop.current()
        tornado.ioloop.IOLoop.instance().stop()

        LOGGER.info("\n[server.main] Server Stopped.")


if __name__ == "__main__":
    main()
