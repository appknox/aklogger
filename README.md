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

logger = aklogger.AKLogger('test', level='DEBUG')
f_handler = aklogger.handlers.FileHandler('test.log')
c_handler = aklogger.handlers.StreamHandler()
s_handler = aklogger.handlers.SlackerLogHandler(token, channel)

logger.add_handler(f_handler)
logger.add_handler(c_handler)
logger.add_handler(s_handler)

logger.error('This is title', 'This is description')
```

See [python logging docs](https://docs.python.org/3/library/logging.html) for more uses.
