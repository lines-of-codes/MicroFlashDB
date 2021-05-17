import json

# data = { 'users': {'18': ':)'}}
data = {
    'serveraddress':"127.0.0.1",
    'serverport':9000,
    'maxquerybytes':512,
    'iptype': 'IPv4',
    'isProtected': False,
    'connpasswd': 'password',
    'dbfiles': [
        'maindb.mfdb'
    ]
}
jsonstring = json.dumps(data, indent=4)
parsedstring = json.loads(jsonstring)

print(jsonstring)
print(parsedstring)