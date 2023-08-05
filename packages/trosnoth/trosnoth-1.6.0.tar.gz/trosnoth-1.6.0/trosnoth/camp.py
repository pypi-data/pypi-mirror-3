import twisted.web.client

AUTH_SCRIPT_PATH = 'http://www.ubertweak.su/includes/trosnoth-check.php'
SHARED_SECRET = 'thisisatest'

def authenticateUser(username, password):
    return twisted.web.client.getPage('%s?username=%s&password=%s' %
            (AUTH_SCRIPT_PATH, username, password), timeout=5)
