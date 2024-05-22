def jwt_response_payload_handler(token, user=None, *args, **kwargs):
    return {
        "token": token,
        "user_id": user.id,
        "role": user.get_roles_str(),
        "full_name": user.fio() if user.fio() != "  " else "",
    }