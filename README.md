# Majira

A command line Jira client (Python 2).

## Installation

Create a virtualenv and install majira inside it via the usual `python setup.py install`.

## Configuration

Create `~/.majirarc`:

```
username = your username
password = your secret password
url = your jira instance URL
```

You can also have several custom *dashboards*; for example this configures a "ticketduty" JQL query
that you can use like this: `majira list ticketduty`:

```
list_ticketduty = project = 11000 AND "Epic Link" is EMPTY AND issuetype != EPIC AND Sprint is EMPTY AND (resolutiondate > startOfWeek() OR resolutiondate is EMPTY) AND status = "To Do Later"
```

Please note that this utility is a work in progress.
