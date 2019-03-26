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
from aklogger import logger

logger.set_name('mycroft')
logger.setLevel('DEBUG')

# This will log to console
logger.info('Some Dummy log', 'Some dummy details of the dummy log')

# Enable File log
logger.log_to_file('file.log')

# This will log to file and console
logger.info('Some Dummy log', 'Some dummy details of the dummy log')

# Enable Slack
logger.enable_slack(SLACK_TOKEN)

# Set slack level
logger.set_slack_level('WARNING')

# Now the logs will be log to slack
logger.warning('Some Dummy log', 'Some dummy details of the dummy log')

# You can also do a force push to slack no matter what the slack level is set.
logger.info('Dummy log', 'Details of the dummy log', force_push_slack=True)
```

See [python logging docs](https://docs.python.org/3/library/logging.html) for more uses.
