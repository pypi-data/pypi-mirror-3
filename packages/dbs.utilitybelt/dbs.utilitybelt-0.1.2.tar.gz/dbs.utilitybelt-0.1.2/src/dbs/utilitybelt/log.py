import os
import logging


BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED,
    'BLACK': BLACK,
    'BLUE': BLUE,
    'CYAN': CYAN,
    'GREEN': GREEN,
    'MAGENTA': MAGENTA,
    'RED': RED,
    'WHITE': WHITE,
    'YELLOW': YELLOW,
}


class ColorFormatter(logging.Formatter):
    """
    Based on http://stackoverflow.com/a/2532931/558194

    To start using set formatter kwarg () to 'utilitybelt.log.ColorLogging'

    E.g.:

    'formatters': {
        'console': {
            '()': 'dbs.utilitybelt.log.ColorFormatter',
            'format': '[$GREEN%(asctime)s$RESET][$COLOR%(levelname)-5s:%(name)s$RESET] %(message)s\n$YELLOW%(filename)s:%(funcName)s:%(lineno)d',
            'datefmt': '%H:%M:%S',
            },
        },

    this class adds aditional tags:

       $COLOR         colors based on logging level
       $BOLD          sets text to be bold
       $RESET         resets color or bold

       $BLACK         sets black color
       $BLUE          sets blue color
       $CYAN          sets cyan color
       $GREEN         sets green color
       $MAGENTA       sets magenta color
       $RED           sets red color
       $WHITE         sets white color
       $YELLOW        sets yellow color

       $BG-BLACK      sets black color background
       $BG-BLUE       sets blue color background
       $BG-CYAN       sets cyan color background
       $BG-GREEN      sets green color background
       $BG-MAGENTA    sets magenta color background
       $BG-RED        sets red color background
       $BG-WHITE      sets white color background
       $BG-YELLOW     sets yellow color background

    """

    def __init__(self, *args, **kwargs):
        # can't do super(...) here because Formatter is an old school class
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        levelname = record.levelname

        if os.name == "posix":
            color = COLOR_SEQ % (30 + COLORS[levelname])
        else:
            color = ''

        message = logging.Formatter.format(self, record)
        message = message.replace("$RESET", RESET_SEQ)\
                           .replace("$BOLD",  BOLD_SEQ)\
                           .replace("$COLOR", color)

        if os.name == "posix":
            for k, v in COLORS.items():
                message = message.replace("$" + k, COLOR_SEQ % (v + 30))\
                                .replace("$BG" + k, COLOR_SEQ % (v + 40))\
                                .replace("$BG-" + k, COLOR_SEQ % (v + 40))
        else:
            for k, v in COLORS.items():
                message = message.replace("$" + k, '')\
                                .replace("$BG" + k, '')\
                                .replace("$BG-" + k, '')

        return message + RESET_SEQ
