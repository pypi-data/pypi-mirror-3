# Python wrapper for the Intercom API.

What follows is a brief introduction to python-intercom. Our [detailed documentation](http://readthedocs.org/docs/python-intercom/ "python-intercom Documentation") is available on http://readthedocs.org.

## Authentication

More information on [docs.intercom.io](http://docs.intercom.io/api#authentication "API Authentication").

    from intercom import Intercom
    Intercom.app_id = 'dummy-app-id'
    Intercom.api_key = 'dummy-api-key'

## Users

### Getting all Users

More information on [docs.intercom.io](http://docs.intercom.io/api#getting_all_users "Getting all Users")

    from intercom import User
    for user in User.all():
        print user.email

### Getting a User

More information on [docs.intercom.io](http://docs.intercom.io/api#getting_a_user "Getting a User")

    user = User.find(email="ben@intercom.io")

### Creating a User

More infomation on [docs.intercom.io](http://docs.intercom.io/api#creating_a_user "Creating a User")

    user = User.create(email="ben@intercom.io",
                       user_id=7902,
                       name="Ben McRedmond",
                       created_at=datetime.now(),
                       custom_data={"plan": "pro"},
                       last_seen_ip="1.2.3.4",
                       last_seen_user_agent="ie6")

### Updating a User

More information on [docs.intercom.io](http://docs.intercom.io/api#updating_a_user "Updating a User")

    user = User.find(email="ben@intercom.io")
    user.name = "Benjamin McRedmond"
    user.save()

## Impressions

### Creating an Impression

More information on [docs.intercom.io](http://docs.intercom.io/api#creating_an_impression "Creating an Impression")

    from intercom import Impression
    impression = Impression.create(email="ben@intercom.io", 
            user_agent="my-awesome-android-app-v0.0.1")

## Message Threads

### Getting Message Threads

More information on [docs.intercom.io](http://docs.intercom.io/api#getting_messages "Getting Message Threads")

    from intercom import MessageThread

    # all message threads
    message_threads = MessageThread.find_all(email="ben@intercom.io")

    # a specific thread
    message_threads = MessageThread.find_all(email="ben@intercom.io",
            thread_id=123)

### Creating a Message Thread

    message_thread = MessageThread.create(email="ben@intercom.io", 
            body="Hey Intercom, What is up?")

### Reply on a Message Thread

    message_thread = MessageThread.create(email="ben@intercom.io",
            thread_id=123,
            body="No much either :(")

