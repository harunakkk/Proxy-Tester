import sys
import aiohttp
import asyncio
import re
from aiohttp.abc import AbstractCookieJar
from aiohttp import DummyCookieJar
from aiohttp_socks import ProxyConnector, ProxyType
animasyon = True

async def read_proxy_list():
    with open("working_proxy_list.txt","r") as file:
        proxy_list = file.read()
    regex = re.compile(
        r"(\b(?:\d{1,3}\.){3}\d{1,3}\b"
        r"):"
        r"(\d{1,5})"
        )
    return re.finditer(regex, proxy_list)

async def animate():
    global animasyon
    animation = "|/-\\"
    idx = 0
    while animasyon:
        sys.stdout.write("\rTesting Proxies... " + animation[idx % len(animation)])
        sys.stdout.flush()
        idx += 1
        await asyncio.sleep(0.1)

async def fetch(client, site, proxy = None):
    try:
        async with client.get(site, proxy=proxy) as resp:
            assert resp.status == 200
            return await resp.text()
    except:
        return None

async def main():
    animation_task = asyncio.create_task(animate())
    global animasyon
    working_proxies = []
    site_list = ["https://spys.me/proxy.txt", "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"]
    i = 0
    working_proxies_count = 0
    cookie_jar: AbstractCookieJar = DummyCookieJar()
    regex = re.compile(
            r"(?:^|\D)?("
            r"(?:[1-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"  # 1-255
            + r"\.(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])" * 3  # 0-255
            + r"):"
            + 
                r"(\b(?:[0-9]|[1-9][0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])\b)" # 0-65535
            + r"(\D{3}[\-][AH][\-][S])?" # AH-S
        )
    working_current_proxies = await read_proxy_list()
    while True:
        try:
            proxy = next(working_current_proxies)
        except:
            break
        async with aiohttp.ClientSession(cookie_jar=cookie_jar, timeout=aiohttp.ClientTimeout(total=5)) as client:
            data = await fetch(client, site = 'https://google.com', proxy = 'http://' + proxy.group(1) + ':' + proxy.group(2))
            data = await fetch(client, site = 'http://ip-api.com/json/?fields=status,message,country,regionName,city,isp,org,proxy,query', proxy = 'http://' + proxy.group(0))
            if data is None:
                continue
            print(data)
            print(proxy.group(0))
            working_proxies.append(proxy.group(0))
            working_proxies_count+=1
    async with aiohttp.ClientSession(cookie_jar=cookie_jar) as client:
        for j in range(len(site_list)):
            if (working_proxies_count>=5):
                break
            proxy_list = await fetch(client,site_list[j])
            if proxy_list is None:
                continue
            proxies = re.finditer(regex, proxy_list)
            for i in re.findall(regex,proxy_list):
                try:
                    proxy = next(proxies)
                except:
                    break
                async with aiohttp.ClientSession(cookie_jar=cookie_jar, timeout=aiohttp.ClientTimeout(total=5)) as client:
                    data = await fetch(client, site = 'https://google.com', proxy = 'http://' + proxy.group(0))
                    data = await fetch(client, site = 'http://ip-api.com/json/?fields=status,message,country,regionName,city,isp,org,proxy,query', proxy = 'http://' + proxy.group(0))
                    if data is None:
                        continue
                    for k in range(len(working_proxies)):
                        if (working_proxies[k] == proxy.group(0)):
                            continue
                    print(proxy.group(0))
                    print(data)
                    working_proxies.append(proxy.group(0))
                    working_proxies_count+=1
                if (working_proxies_count>=5):
                    break
    open("working_proxy_list.txt","w").close()
    with open("working_proxy_list.txt","w") as file:
        for i in range(len(working_proxies)):
            file.write(working_proxies[i] + "\n")
    animasyon = False
    if(working_proxies_count == 0):
        print("\nCouldn't find proxy.")
    else:
        print("\n" + str(working_proxies_count) + " proxies written to ./working_proxy_list.txt")

asyncio.run(main())