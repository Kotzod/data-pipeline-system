#!/usr/bin/env python
import os
os.environ['LUIGI_CONFIG_PATH'] = 'luigi.cfg'

from tornado.ioloop import IOLoop
import luigi.server
import luigi.scheduler

if __name__ == '__main__':
    print("=" * 60)
    print("Luigi server starting on http://localhost:8082")
    print("Open your browser to see the task visualization UI!")
    print("=" * 60)

    scheduler = luigi.scheduler.Scheduler()
    tornado_app = luigi.server.app(scheduler)
    tornado_app.listen(8082, address='localhost')
    IOLoop.current().start()
