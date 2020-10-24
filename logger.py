import pendulum

class LogColor(object):
    """A class for defining a color for log printing

    NOTE: only certain shells allow support for RGB colors, if your shell
    does not allow for the custom colors, use the 'code' parameter to 
    pass in one of the defalt values
    """

    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    PURPLE = 35
    TEAL = 36
    WHITE = 37

    SPACE = ' '
    NEW_LINE = '\n'

    END_FORMAT = '\033[0m'

    def __init__(
        self, 
        red=None, 
        green=None, 
        blue=None, 
        code=None,
        bold=False, 
        italic=False, 
        underline=False,
        blink=False, 
        strikethrough=False, 
        invert=False,
    ):

        super(LogColor, self).__init__()
        self.__color = '\033[0'
        if red != None and green != None and blue != None:
            self.__color = f'\033[38;2;{red};{green};{blue}'
        elif code:
            self.__color = f'\033[{code}'

        self.__bold = bold
        self.__italic = italic
        self.__underline = underline
        self.__blink = blink
        self.__strikethrough = strikethrough

        mods = ''
        if bold:
            mods += ';1'
        if italic:
            mods += ';3'
        if underline:
            mods += ';4'
        if blink:
            mods += ';5'
        if strikethrough:
            mods += ';9'
        if invert:
            mods += ';7'
        self.__preformated = self.__color + mods + 'm'

    def change_color(self, red=None, green=None, blue=None, code=None):
        self.__color = '\033[0'
        if red and green and blue:
            self.__color = f'\033[33;2;{red};{green};{blue}'
        elif code:
            self.__color = f'\033[{code}'


    def standard(self, *args, join=' '):
        return self.__format(self.__preformated, args, self.END_FORMAT, join=join)

    def plain(self, *args, join=' '):
        return self.__format(self.__color+'m', args, self.END_FORMAT, join=join)

    def format(
        self,
        text, 
        bold=False, 
        italic=False, 
        underline=False,
        blink=False, 
        strikethrough=False, 
        invert=False,
    ):
        """Formats a string to new setitngs.

        This is a more expensive operation, but offers flexibility for 
        one-time format changes.
        """
        mods = ''
        if bold:
            mods += ';1'
        if italic:
            mods += ';3'
        if underline:
            mods += ';4'
        if blink:
            mods += ';5'
        if strikethrough:
            mods += ';9'
        if invert:
            mods += ';7'
        return f'{self.__color}{mods}m{text}{self.END_FORMAT}'

    def __format(self, start, text, end, join=SPACE): 
        return start + join.join(text) + end

class Logger(object):
    """A class that speeds up logging for a game engine.

    This class is intended to help reduce the lag that can be introduced
    by constantly logging output to the console. By capturing logs to 
    memory and printing in bulk, less often, on demand, there should be 
    fewer lagging frames.

    For example:
    If you have a lot of debug statements printing in each frame (such as 
    object location info, etc.) 
    """

    __DEFAULT_DEBUG_LOG_COLOR = LogColor(33, 192, 232, italic=True)
    __DEFAULT_INFO_LOG_COLOR = LogColor(222, 222, 222)
    __DEFAULT_WARNING_LOG_COLOR = LogColor(255, 245, 23, bold=True)
    __DEFAULT_ERROR_LOG_COLOR = LogColor(241, 25, 44, bold=True)
    __DEFAULT_CRITICAL_LOG_COLOR = LogColor(
        red=241, 
        green=25, 
        blue=44, 
        bold=True, 
        invert=True
    )

    __DEFAULT_FUNCTIONS = [
        {   
            'name': 'Debug',
            'level': 0,
            'color': __DEFAULT_DEBUG_LOG_COLOR,
        },
        {
            'name': 'Info',
            'level': 25,
            'color': __DEFAULT_INFO_LOG_COLOR,
        },
        {
            'name': 'Warning',
            'level': 50,
            'color': __DEFAULT_WARNING_LOG_COLOR,
        },
        {
            'name': 'Error',
            'level': 75,
            'color': __DEFAULT_ERROR_LOG_COLOR,
        },
        {
            'name': 'Critical',
            'level': 100,
            'color': __DEFAULT_CRITICAL_LOG_COLOR,
            'force_immideate_print': True
        },
    ]

    __NEW_LINE = '\n'

    def __init__(
        self, 
        level=0, 
        initial_logging_functions=None, 
        real_time=False, 
        log_file=None,
        suppress_default_logger_warnings=False,
        suppress_default_logger_errors=False,
    ):
        super(Logger, self).__init__()
        self.__log_queue = []
        self.__level = level
        self.__queued_msg = ''

        self.__suppress_default_logger_warnings = (
            suppress_default_logger_warnings
        )
        self.__suppress_default_logger_errors = suppress_default_logger_errors

        if initial_logging_functions == None:
            initial_logging_functions = self.__DEFAULT_FUNCTIONS
        for value in initial_logging_functions:
            self.add_logging_type(
                name=value.get('name'),
                level=value.get('level'),
                color=value.get('color'),
                force_immideate_print=value.get(
                    'force_immideate_print', 
                    False,
                )
            )

    def cycle_print(self):
        if self.__queued_msg:
            self.__execute_print()
        else:
            self.__prepare_print()

    def print(self):
        self.__prepare_print()
        self.__execute_print()

    def add_logging_type(self, name, level, color, force_immideate_print=False):
        if name[0:2] == '__':
            self.__logger_warning(
                'LOGGER WARNING::DYNAMIC LOGGERS ARE NOT PRIVATE, THIS '
                'LOGGER MAY BEHAVE DIFFERENTLY THAN EXPECTED.'
            )
        def dynamic_logger(*args, join=' '):
            if level >= self.__level:
                now = pendulum.now()
                meta_data = f'[ {now.to_day_datetime_string()} - {name} ]:'
                self.__log(
                    message=color.standard(meta_data, *args, join=join),
                    level=level,
                )
                if force_immideate_print:
                    self.print()

        dynamic_logger.__name__ = name
        setattr(self, name.casefold(), dynamic_logger)

    def __log(self, message, level):
        if level >= self.__level:
            self.__log_queue.append(message)


    def __prepare_print(self):
        if len(self.__log_queue) > 0:
            if self.__queued_msg != '':
                self.__queued_msg += '\n'
            self.__queued_msg += (
                self.__NEW_LINE.join(self.__log_queue)
            )
            self.__log_queue = []

    def __execute_print(self):
        if self.__queued_msg:
            print(self.__queued_msg)
            self.__queued_msg = ''

    def __logger_warning(self, text):
        if not self.__suppress_default_logger_warnings:
            print(
                self.__DEFAULT_WARNING_LOG_COLOR.standard(text)
            )

    def __logger_error(self, text):
        if not self.__suppress_default_logger_errors:
            print(
                self.__DEFAULT_ERROR_LOG_COLOR.standard(text)
            )
