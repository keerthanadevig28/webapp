import statsd
import time
from contextlib import contextmanager


# StatsD client — sends metrics to CloudWatch Agent on port 8125
client = statsd.StatsClient(
    host="localhost",
    port=8125,
    prefix="csye6225"
)


def count(metric_name: str):
    """Increment a counter — use this for every API call count"""
    client.incr(metric_name)


@contextmanager
def timed(metric_name: str):
    """
    Context manager to time any block of code in milliseconds.
    
    Usage:
        with timed("db.get_user"):
            result = db.query(User).filter_by(id=user_id).first()
    """
    start = time.time()
    try:
        yield
    finally:
        elapsed = (time.time() - start) * 1000
        client.timing(metric_name, elapsed)
