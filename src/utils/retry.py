import time


def retry(exceptions=(Exception), max=3, delay=3, backoff=1):
    def decorator(callback):
        def wrapper(*args, **kwargs):
            attempts = 0

            while (max - attempts) > 0:
                try:
                    return callback(*args, **kwargs)

                except exceptions as exception:
                    sleep = delay ** (backoff * attempts)

                    print('retry exception:\n\t{}\n\tattempts: {}\n\tsleep: {}'.format(
                        exception, attempts, sleep))

                    attempts += 1
                    time.sleep(sleep)

            return callback(*args, **kwargs)
        return wrapper
    return decorator
