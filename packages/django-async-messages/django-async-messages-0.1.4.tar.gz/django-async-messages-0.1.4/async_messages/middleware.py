from django.contrib import messages

from async_messages import get_message


class AsyncMiddleware(object):

    def process_response(self, request, response):
        # Check for message for this user and, if it exists,
        # call the messages API with it
       if hasattr(request, "session") and request.user.is_authenticated():
            msg, level = get_message(request.user)
            if msg:
                messages.add_message(request, level, msg)
       return response
