from flask import Flask
from redis import Redis
import logging
import json_log_formatter
import os

from ddtrace import tracer, patch_all
from datadog import initialize, statsd

patch_all()
initialize(statsd_host=os.environ.get('DATADOG_STATSD_HOST'))
tracer.set_tags({ 'app':'redis-flask-app', 'env':'azure_demo'})

formatter = json_log_formatter.JSONFormatter()

json_handler = logging.FileHandler(filename='/var/log/my-log.json')
json_handler.setFormatter(formatter)

logger = logging.getLogger('my_json')
logger.addHandler(json_handler)
logger.setLevel(logging.INFO)

app = Flask(__name__)
redis = Redis(host='redis', port=6379)

@tracer.wrap()
@app.route("/")
def hello():
    # Increment the Datadog counter.
    logger.info('Sign up', extra={'referral_code': 'garner1234'})
    statsd.increment('app.hello', tags=['test:garner'])

    redis.incr('hits')
    return 'Hello World! I have been seen %s times.' % redis.get('hits')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
