from User.models import User
from e_bidding.api_render import api_response_render
import functools

def auth_required():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self,request, *args, **kwargs):
            if 'HTTP_AUTHORIZATION' in request.META:
                user = User.user_from_token(
                    request.META['HTTP_AUTHORIZATION'].split(" ")[1])
            else:
                if 'access_token' not in request.COOKIES:
                    return api_response_render(status_msg="Authentication failed for user, please login",
                                    status_type="ERROR", status_code=401)
                token = request.COOKIES['access_token']
                user = User.user_from_token(token)
            if user['user_id'] is not None:
                return func(self, request, user['user_id'], **kwargs)
            else:
                return api_response_render(status_msg="Authentication failed for user, please login",
                                    status_type="ERROR", status_code=401)
        return wrapper
    return decorator
