# aklogger

Keep track of all the events happening in your project: A generic logging package for python projects.

## [Features]

- Logging to console
- Logging to file
- Push logs to slack

## Installation

```
$ pip install aklogger
```

## Usage

Following script will log messages to slack, file and console:

```python
import aklogger

token = SLACK_API_KEY
channel = CHANNEL_NAME

logger = aklogger.aklogger.Logger('test', level='DEBUG')
f_handler = aklogger.handlers.FileHandler('test.log')
c_handler = aklogger.handlers.StreamHandler()
s_handler = aklogger.handlers.SlackerLogHandler(token, channel)

logger.addHandler(f_handler)
logger.addHandler(c_handler)
logger.addHandler(s_handler)

logger.error('aklogger is loggggggggggggggggggggging')
```

See [python logging docs](https://docs.python.org/3/library/logging.html) for more uses.
