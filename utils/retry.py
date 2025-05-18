import time

def try_with_retries(func, attempts=5, delay=5, *args, **kwargs):
    """
    Repeatedly calls `func(*args, **kwargs)` until it returns a non-None result
    or the max number of attempts is reached.

    Parameters:
        func (callable): The function to call.
        attempts (int): Max number of attempts.
        delay (int): Delay in seconds between failed attempts.
        *args, **kwargs: Passed to the function.

    Returns:
        The first non-None result or None if all fail.
    """
    for i in range(attempts):
        result = func(*args, **kwargs)
        if result is not None:
            return result
        if i < attempts - 1:
            print(f"Attempt {i+1} failed, retrying in {delay} seconds...")
            time.sleep(delay)
    return None
