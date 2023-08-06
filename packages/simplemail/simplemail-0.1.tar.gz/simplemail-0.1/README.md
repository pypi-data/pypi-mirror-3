# simplemail

## Overview
**simplemail** is an easy way to send emails in Python. It will use a sendmail binary which is almost always available and ready to go.

## Dependancies
- Python 2.6 or 2.7

## Sample usecase
The code has docstrings which explains how to use the library. But here's the sample usecase I just made up for showing you the benefits and simplicity of using it.

Let's assume that you have a general announcement which you would like to send out to your mailing list. The message itself is common for every member of your list, but you want to greet every person by his or her name in the beginning of your message.

So you have a list of your customer in a dictionary.

    from simplemail import Simplemail

    mailinglist = {"Bob": "bob@domain.tld",
                   "Alice": "alice@domain.tld"}

Let's fire the default settings for all our emails.

    message = Simplemail(sender="Maillist Owner <postmaster@domain.tld>",
                         subject="Monthly announcement")

Next you are going to write a default message body for everyone.

    body = "We are proudly to present our new feature."

Let's compose a personal greeting for every member of your list and fire an email.

    for person in mailinglist.keys():
        gr = "Hello, %s\n\n%s" % (person, body)
        message.send(recipient=mailinglist[person], body=gr)

Now you have a personal greeting for all of your subscribers.

## Downloads
This library is available at [PyPi](http://pypi.python.org/pypi/simplemail).