__author__          = 'agsvn'

import requests
import base64
import json
import uuid
import yaml
import zlib

riotClientVersion   = "18.3.0"
manifestVersion     = "0.0.0.206" # 9.13

class call:
    def __init__(self):
        self.openid = self.getConfiguration(self)
        self.system = self.getSystem('live', manifestVersion)

        self.dsid = uuid.uuid4().hex
        self.supportedRegions = self.openid["riot_lol_regions_supported"]
        self.tokenEndpoint = self.openid["token_endpoint"]
        self.userinfoEndpoint = self.openid["userinfo_endpoint"]

    def inventory(self, inventoryType: str=None):
        headers = {
            'Accept-Encoding': 'deflate, gzip',
            'user-agent': self.userAgent('inventory'),
            'Accept': 'application/json',
            'Authorization': 'Bearer {0}'.format(self.idToken)
        }

        r = requests.get('https://{0}.cap.riotgames.com/lolinventoryservice/v2/inventoriesWithLoyalty?puuid={1}&inventoryTypes={2}&location={3}&accountId={4}&signed=true'
            .format(self.platform, self.puuid, inventoryType, self.serviceLocation, self.accountId), headers=headers)

        #print(r.request.url)
        #print(r.request.headers)
        #print(r.request.body)

        _response = r.json()
        return json.loads(base64.b64decode(self.fixTokenPayload(_response["data"]["itemsJwt"].split('.')[1])))
        
    def token(self, username: str=None, password: str=None, region: str=None):
        self.lcuToken = self.system["region_data"][region]["rso"]["token"]
        self.platform = self.system["region_data"][region]["rso_platform_id"]
        self.lqUrl = self.system["region_data"][region]["servers"]["lcds"]["login_queue_url"]
        self.serviceLocation = self.system["region_data"][region]["servers"]["discoverous_service_location"]

        if self.platform in self.supportedRegions:
            headers = {
                'Accept-Encoding': 'deflate, gzip', 
                'user-agent': self.userAgent('rso'), 
                'Cache-Control': 'no-cache', 
                'Content-Type': 'application/x-www-form-urlencoded', 
                'X-Riot-DSID': self.dsid, 
                'Accept': 'application/json'
            }
            
            payload = {
                'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
                'client_assertion': self.lcuToken,
                'grant_type': 'password',
                'username': '{0}|{1}'.format(self.platform, username),
                'password': password,
                'scope': 'openid offline_access lol ban profile email phone'
            }

            r = requests.post(self.tokenEndpoint, headers=headers, data=payload)
            
            #print(r.request.url)
            #print(r.request.headers)
            #print(r.request.body)
            
            if r.status_code == 200:
                self.accessToken = r.json()["access_token"]
                self.idToken = r.json()["id_token"]
                
                _accessTokenPayload = json.loads(base64.b64decode(self.fixTokenPayload(self.accessToken.split('.')[1])))
                
                self.puuid = _accessTokenPayload["sub"]
                self.accountId = _accessTokenPayload["dat"]["u"]
            elif 'invalid_credentials' in r.text:   raise Exception("invalid credentials")
            elif 'rate_limited' in r.text:          raise Exception("too many requests, your ip has been banned for 3 minutes")
            else:                                   raise Exception("unknown error")
        else:
            raise Exception("region is not supported")

    def getSystem(self, patchline: str=None, release: str=None):
        if patchline is not None and release is not None:
            r = requests.get('http://l3cdn.riotgames.com/releases/{0}/projects/league_client/releases/{1}/files/system.yaml.compressed'.format(patchline, release))
            if r.status_code is 200:
                return yaml.load(zlib.decompress(r.content), Loader=yaml.FullLoader)
            else: 
                raise Exception("couldn't obtain lcu configuration")
        else: 
            raise Exception("patchline and solution manifest version was not provided")

    @staticmethod
    def getConfiguration(self):
        headers = {
            'Accept-Encoding': 'deflate, gzip', 
            'user-agent': self.userAgent('rso'), 
            'Accept': 'application/json'
        }

        #print(r.request.url)
        #print(r.request.headers)
        #print(r.request.body)

        r = requests.get('https://auth.riotgames.com/.well-known/openid-configuration', headers=headers)
        
        if r.status_code is 200:
            return r.json()
        else: 
            raise Exception("couldn't obtain openid configuration")

    @staticmethod
    def fixTokenPayload(token: str=None):
        if token is not None:
            token += "=" * (len(token) % 4)
            return token
        else:
            raise Exception("token payload is empty")

    @staticmethod
    def userAgent(type: str=None):
        if type is not None: 
            plugin = {
                'rso': 'lol-rso-auth',
                'inventory': 'lol-inventory',
                'login': 'lol-login'
            }[type]
            return 'RiotClient/{0} ({1})'.format(riotClientVersion, plugin)
        else:
            raise Exception('requester is not specified')

if __name__ == '__main__':
    call = call()
    call.token("username", "password", "EUNE")
    championCount = len(call.inventory("CHAMPION")["items"]["CHAMPION"])
    print("summoner has {0} champions".format(championCount))