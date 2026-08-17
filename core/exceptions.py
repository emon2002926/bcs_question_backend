from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_messages = []
        message = "An error occurred"

        if isinstance(response.data, dict):
            for field, errors in response.data.items():
                if field in ['detail', 'error']:
                    msg = str(errors)
                    message = msg
                    error_messages.append({
                        "path": "",
                        "message": msg
                    })
                elif isinstance(errors, list):
                    for err in errors:
                        msg = str(err)
                        error_messages.append({
                            "path": field,
                            "message": msg
                        })
                elif isinstance(errors, dict):
                    for sub_field, sub_errors in errors.items():
                        if isinstance(sub_errors, list):
                            for sub_err in sub_errors:
                                error_messages.append({
                                    "path": f"{field}.{sub_field}",
                                    "message": str(sub_err)
                                })
                        else:
                            error_messages.append({
                                "path": f"{field}.{sub_field}",
                                "message": str(sub_errors)
                            })
                else:
                    msg = str(errors)
                    error_messages.append({
                        "path": field,
                        "message": msg
                    })

            if error_messages and message == "An error occurred":
                message = error_messages[0]["message"]

        elif isinstance(response.data, list):
            for err in response.data:
                msg = str(err)
                error_messages.append({
                    "path": "",
                    "message": msg
                })
            if error_messages:
                message = error_messages[0]["message"]
        else:
            message = str(response.data)
            error_messages.append({
                "path": "",
                "message": message
            })

        response.data = {
            "success": False,
            "message": message,
            "errorMessages": error_messages
        }

    return response
