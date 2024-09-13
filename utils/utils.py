import sys
import os
import hashlib
import functools


def listen_error(exception, on_error=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                return func(*args, **kw)
            except exception:
                if on_error is not None:
                    on_error()
                sys.exit(1)

        return wrapper

    return decorator


def string_to_md5(string):
    md5 = hashlib.md5()
    md5.update(string.encode("utf-8"))
    return md5.hexdigest()


def show_banner(text="ILP"):
    print(
        "\n ___ _     ____\n|_ _| |   |  _ \\\n | || |   | |_) |\n | || |___|  __/\n|___|_____|_|"
    )


def set_title(text="ILP"):
    os.system("title " + text)


if __name__ == "__main__":
    show_banner()
