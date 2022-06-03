import Crypto.PublicKey.ElGamal as elg
import json
from os import urandom
print('start generating..')
privkey = elg.generate(1024,urandom)
obj = {'P':int(privkey.p),'G':int(privkey.g),'Y':int(privkey.y),'X':int(privkey.x)}

#store to db
with open('../settings.json','r') as f:
    settings = json.loads(f.read())
    settings["KEY"] = obj

with open('../settings.json','w') as f:
    f.write(json.dumps(settings, sort_keys=True, indent=4))