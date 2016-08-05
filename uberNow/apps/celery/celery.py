from celery import Celery

app = Celery('tasks',
             broker='ampq://guest:guest@localhost:5672',
             include=['celery.email_tasks', 'celery.uber_task', 'celery.maps_task']
             )

app.config_from_object('celeryconfig')


if __name__ == '__main__': 
	app.worker_main()
