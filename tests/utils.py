import secrets
import string


def unique_username_email():
    alphabet = string.ascii_lowercase + string.digits
    unique_username = "testuser_" + "".join(secrets.choice(alphabet) for _ in range(8))
    unique_email = "".join(secrets.choice(alphabet) for _ in range(10)) + "@example.com"
    return unique_username, unique_email


def unique_blog_title():
    alphabet = string.ascii_letters + string.digits
    unique_title = "Test post " + "".join(secrets.choice(alphabet) for _ in range(8))
    return unique_title
