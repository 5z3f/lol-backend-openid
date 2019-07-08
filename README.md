# lol-backend-openid
LeagueClient openid calls for rso authorization and summoner data gathering

*Production platform IDs (riot):*  
EUN1, RU, NA1, KR, TR1, JP1, OC1, BR1, EUW1, LA1 (LAN), LA2 (LAS), PBE1

**LeagueClient 9.13.280.4632-prod**

## 1. OpenID Configuration

```
GET /.well-known/openid-configuration HTTP/1.1
Host: auth.riotgames.com
Accept-Encoding: deflate, gzip
user-agent: RiotClient/18.3.0 (lol-rso-auth)
Accept: application/json
```

## 2. Authorization Token
```
POST /token HTTP/1.1
Host: auth.riotgames.com
Accept-Encoding: deflate, gzip
user-agent: RiotClient/18.3.0 (lol-rso-auth)
Cache-Control: no-cache
Content-Type: application/x-www-form-urlencoded
X-Riot-DSID: {UUID v4 without dash}
Accept: application/json
Content-Length: {Request body length}

client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer&
client_assertion={token}&
grant_type=password&
username={platformId}%7C{USERNAME}&
password={PASSWORD}&
scope=openid%20offline_access%20lol%20ban%20profile%20email%20phone
```
### Response
```
200 OK                                  | {"access_token":"{accessToken}","token_type":"Bearer","expires_in":600,"refresh_token":"ec1:{refreshToken}","id_token":"{idToken}","scope":"openid offline_access lol ban profile email phone summoner"}
400 Bad Request / 429 Too Many Requests | {"error":"invalid_grant","error_description":"{errorType}"}
401 Unauthorized                        | 0 Length Body
```

#### errorType
*   invalid_credentials
*   account_state_disabled
*   account_state_transferring_out
*   account_state_transferred_out
*   account_state_platform_split
*   account_state_transferring_in
*   account_state_transferring_back
*   account_state_creating
*   account_state_archived
*   account_state_pending_forget **(server side only)**
*   rate_limited **(server side only)**
*   consent_required **(client side only)**

### accessToken payload
```
{
  "sub": "{puuid}",
  "scp": [
    "openid",
    "offline_access",
    "lol",
    "ban",
    "profile",
    "email",
    "phone",
    "summoner"
  ],
  "clm": [
    "rgn_{platformId}",
    "pw",
    "lol",
    "original_platform_id",
    "original_account_id",
    "ban",
    "acct_gnt",
    "lol_account",
    "openid",
    "photo",
    "ppid",
    "region",
    "pvpnet_account_id",
    "acct",
    "username",
    "!_v8H"
  ],
  "dat": {
    "r": "{platformId}",
    "c": "ec1",
    "u": {accountId}
  },
  "iss": "https://auth.riotgames.com",
  "exp": {expirationTime},
  "iat": {issuedAt},
  "jti": "{uniqueJwtIdentifier}",
  "cid": "lol"
}
```
### idToken payload
```
{
  "at_hash": "{accessTokenHash}",
  "sub": "{subject}",
  "aud": "lol",
  "country": "{country}",
  "amr": [
    "riot"
  ],
  "iss": "https://auth.riotgames.com",
  "lol": [
    {
      "uid": {originalAccountId},
      "cuid": {currentAccountId},
      "uname": "{USERNAME}",
      "cpid": "{currentPlatformId}",
      "ptrid": "{originalPlatformId}",
      "pid": "{platformId}",
      "state": "ENABLED"
    }
  ],
  "exp": {expirationTime},
  "iat": {issuedAt},
  "acct": {
    "game_name": null,
    "tag_line": null
  },
  "login_country": "{country}"
}
```

## 3. RSA-OAEP encrypted LCU RSO token for some OpenID and LCDS calls
```
GET /userinfo HTTP/1.1
Host: auth.riotgames.com
Accept-Encoding: deflate, gzip
user-agent: RiotClient/18.3.0 (lol-rso-auth)
Authorization: Bearer {accessToken}
```
### Response
```
200 OK                                  | {userInfo}
```
## 4. RSO Login Queue
```
POST /login-queue/rest/queues/lol/authenticate/RSO HTTP/1.1
Host: lq.{platformId}.lol.riotgames.com
Accept-Encoding: deflate, gzip
user-agent: RiotClient/18.3.0 (lol-login)
Authorization: Bearer {accessToken}
Content-Type: application/x-www-form-urlencoded
Accept: application/json
Content-Length: {Request body length} 

userInfo={userInfo}
```
### Response
```
200 OK | {"reason":"login_rate","delay":11000,"rate":93,"inGameCredentials":{"inGame":false,"summonerId":null,"serverIp":null,"serverPort":null,"encryptionKey":null,"handshakeToken":null},"user":"{USERNAME}","lqt":{"account_id":{accountId},"account_name":"{USERNAME}","other":"{encryptedOtherVar},"fingerprint":"{fingerprint}","signature":"{signature}","timestamp":1562125621764,"uuid":"{UUID v4}","ip":"{IP}","partner_token":"Bearer {accessToken}","resources":"lol"},"status":"LOGIN"}
```

## 5. xx

## 6. xx

## 7. Summoner Inventory
```
GET /lolinventoryservice/v2{inventoryCallType}?puuid={puuid}&inventoryTypes={inventoryType}&location={discoverous_service_location}&accountId={accountId}&signed=true HTTP/1.1
Host: {platformId}.cap.riotgames.com
Accept-Encoding: deflate, gzip
user-agent: RiotClient/18.3.0 (lol-inventory)
Authorization: Bearer {idToken}
```

#### inventoryCallType
*   /inventories **(not in use)**
*   /inventoriesWithLoyalty
*   /inventories/simple

#### inventoryType
*   TOURNAMENT_TROPHY
*   TOURNAMENT_FLAG
*   TOURNAMENT_FRAME
*   TOURNAMENT_LOGO
*   GEAR
*   SKIN_UPGRADE_RECALL
*   SPELL_BOOK_PAGE
*   BOOST
*   BUNDLES
*   CHAMPION
*   CHAMPION_SKIN
*   EMOTE
*   GIFT
*   HEXTECH_CRAFTING
*   MYSTERY
*   RUNE
*   STATSTONE
*   SUMMONER_CUSTOMIZATION
*   SUMMONER_ICON
*   TEAM_SKIN_PURCHASE
*   TRANSFER
*   COMPANION
*   TFT_MAP_SKIN
*   WARD_SKIN
*   AUGMENT_SLOT


### Response
```
200 OK | {"data":{"puuid":"{puuid}","accountId":{accountId},"expires":"{expiresAt}","items":{},"itemsJwt":"{itemsJwt}"}}
```

#### itemsJwt (/inventoriesWithLoyalty, CHAMPION)
```
{
  "shardId": "{platformId}",
  "sub": "{puuid}",
  "exp": {expirationTime},
  "items": {
    "CHAMPION": [
      {
        "itemId": {itemId},
        "inventoryType": "CHAMPION",
        "expirationDate": null,
        "purchaseDate": "{purchaseDate}",
        "quantity": 1,
        "ownedQuantity": 1,
        "usedInGameDate": "{lastUsedDate}",
        "entitlementId": null,
        "entitlementTypeId": "{itemUUIDv4}",
        "instanceId": null,
        "instanceTypeId": "{instanceUUIDv4}",
        "payload": null,
        "f2p": false,
        "rental": false,
        "loyalty": false,
        "wins": null
      },
      ...
    ]
  },
  "iat": {issuedAt}
}
```
## 8. xx

## 9. xx

## 10. xx

## 11. xx
