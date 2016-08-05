#!usr/bin/env python

from tornadomail import send_mail
from tornadomail.backends.smtp import EmailBackend

from tornado import stack_context
from .celery import app
import uberNow.utils


LOGGER = uberNow.utils.LOGGER

class Email():

	def __init__(self, host='smtp.gmail.com', port=587, username=None, password=None, fro=None, to=None):
		self.host = host
		self.port = port
		self.username = username
		self.password = password
		self.client = None
		self.fro = fro 
		self.to = to


	def callback(self, msg, *args, **kwargs):
	    LOGGER.info('Email sent from: %s to: %s ' % (self.fro, self.to))


	def error_handler(self, e, msg, traceback):
	    LOGGER.error('Error %s while Sending email from: %s to: %s ' % (e, self.fro, self.to))



	def send(self, subject='Uber Now', body='Its time to book Uber'):

		with stack_context.ExceptionStackContext(self.error_handler):
			send_mail(
                            str(subject), str(body), self.fro,
                            [self.to], callback=self.callback,
                            connection=EmailBackend(
                                self.host, self.port, self.username, self.password,
                                True
                            )
                        )




@app.task
def send_email(fro, to): 
	e = Email(fro=fro, to=to)
	e.send(fro, to)

