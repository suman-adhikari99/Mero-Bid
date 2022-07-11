from rest_framework.response import Response

def api_response_render(data=None, status_code=None, status_msg=None, status_type=None):
    response_dict = {
        'status': {
            'status_code': status_code,
            'status_message': status_msg,
            'status_type': status_type
        },
        'data': data,
    }
    return Response(response_dict, status=status_code)