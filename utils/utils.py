import os
import pyfiglet


def show_banner(text="ILP"):
    banner = pyfiglet.figlet_format(text)
    print("\n", banner)


def set_title(text="ILP"):
    os.system("title "+text)
