# bitcoin-OTC-trust-API
C. Papathanasiou 2015

For a project,  I needed an API to obtain #bitcoin-otc trust scores. Such an API is not publicly accessible, so I decided to build one instead based on source code of the #bitcoin-otc Gribble bot:
<br>
https://github.com/nanotube/supybot-bitcoin-marketmonitor/blob/master/RatingSystem/plugin.py

The API server depends on:
Python Tornado
MySQLdb
sqlite3


Everything else should be pretty standard.

Requires access to a daily dump of the RatingSystem.db sqlite3 db which can be found here:
<br>
http://bitcoin-otc.com/otc/
<br>
I suggest you have a cronjob which dumps this nightly.


To start API server:
```
Christian-Papathanasious-iMac:Desktop chris$ python otc.py 

```

To issue a request:
HTTP POST to <i>/gettrust</i> with <i>from_nick</i> and <i>to_nick</i> parameters set to the two counterparties whose trust levels you wish to obtina.

<b>Request</b>
```
POST /gettrust HTTP/1.1
Host: localhost:8000
Content-Length: 34
Accept-Encoding: gzip, deflate
Accept: */*
User-Agent: python-requests/2.4.3 CPython/2.7.6 Darwin/14.0.0
Connection: keep-alive
Content-Type: application/x-www-form-urlencoded

to_nick=BigBitz&from_nick=nanotube

```

<b>Response</b>
```
HTTP/1.1 200 OK
Date: Mon, 26 Jan 2015 13:00:59 GMT
Content-Length: 108
Content-Type: text/html; charset=UTF-8
Server: TornadoServer/3.1.1

[{"result": "success", "from_nick": "nanotube", "to_nick": "BigBitz", "L1": 1, "L2": 34, "connections": 21}]
```


