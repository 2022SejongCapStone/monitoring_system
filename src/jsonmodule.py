import os
import json

secret_file = os.path.join("../", 'settings.json')
with open(secret_file, 'r') as f:
    secrets = json.loads(f.read())
 
def get_secret(setting):
        try:
            return secrets[setting]
        except KeyError:
            error_msg = "Set the {} environment variable".format(setting)
            raise ImproperlyConfigured(error_msg)

if __name__ == "__main__":
    print(get_secret("STARTURL"))
    print(get_secret("USERINFO")["ID"])