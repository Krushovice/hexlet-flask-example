def validate_post(name, post):
    if len(name) < 4 and len(post) < 10:
        return False

    return True
