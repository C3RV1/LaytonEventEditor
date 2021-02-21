import colorama


class Debug(object):
    def __init__(self):
        pass

    @staticmethod
    def log(log_message, origin):
        if isinstance(origin, str):
            msg = f"[{origin}] {log_message}"
        else:
            msg = f"[{type(origin).__name__}] {log_message}"
        print(colorama.Fore.WHITE + msg)

    @staticmethod
    def log_error(log_message, origin):
        if isinstance(origin, str):
            msg = f"[{origin}] {log_message}"
        else:
            msg = f"[{type(origin).__name__}] {log_message}"
        print(colorama.Fore.RED + msg)

    @staticmethod
    def log_warning(log_message, origin):
        if isinstance(origin, str):
            msg = f"[{origin}] {log_message}"
        else:
            msg = f"[{type(origin).__name__}] {log_message}"
        print(colorama.Fore.YELLOW + msg)

    @staticmethod
    def log_debug(log_message, origin):
        if isinstance(origin, str):
            msg = f"[{origin}] {log_message}"
        else:
            msg = f"[{type(origin).__name__}] {log_message}"
        print(colorama.Fore.GREEN + msg)
