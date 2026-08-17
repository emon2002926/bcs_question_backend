from rest_framework.response import Response
from rest_framework import status


def send_response(success=True, message="", data=None, status_code=status.HTTP_200_OK):
    """
    Standardized success response format:
    {
        "success": true,
        "message": "...",
        "data": ...
    }
    """
    response_payload = {
        "success": success,
        "message": message,
        "data": data
    }
    return Response(response_payload, status=status_code)


def send_error(message="An error occurred", path="", error_messages=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Standardized error response format:
    {
        "success": false,
        "message": "...",
        "errorMessages": [
            {
                "path": "field_name",
                "message": "..."
            }
        ]
    }
    """
    if error_messages is None:
        error_messages = [
            {
                "path": path,
                "message": message
            }
        ]
    
    return Response({
        "success": False,
        "message": message,
        "errorMessages": error_messages
    }, status=status_code)
