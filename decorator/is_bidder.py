import functools
from User.models import User, UserRole
from e_bidding.api_render import api_response_render


def is_bidder():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            token = request.COOKIES['access_token']
            user = User.user_from_token(token)
            user_role = UserRole.objects.get(user_id=user["user_id"])
            if user_role.role.name == "Bidder":
                return func(self, request, user['user_id'], **kwargs)
            return api_response_render(status_msg="Unauthorized Access", status_type='Error', status_code=400)
        return wrapper
    return decorator
