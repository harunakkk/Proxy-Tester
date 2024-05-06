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

async def fetch(client,site):
    async with client.get(site) as resp:
        assert resp.status == 200
        return await resp.text()

async def main():
    animation_task = asyncio.create_task(animate())
    global animasyon
    working_proxies = []
    i = 0
    working_proxies_count = 0
    cookie_jar: AbstractCookieJar = DummyCookieJar()
    regex = re.compile(
            r"(?:^|\D)?("
            r"(?:[1-9]|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])"  # 1-255
            + r"\.(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])" * 3  # 0-255
            + r"):"
            + (
                r"(\d|[1-9]\d{1,3}|[1-5]\d{4}|6[0-4]\d{3}"
                r"|65[0-4]\d{2}|655[0-2]\d|6553[0-5])"
            )  # 0-65535
            + r"\D{3}[\-][AH][\-][S]"
        )
    async with aiohttp.ClientSession(cookie_jar=cookie_jar) as client:
        proxy_list = await fetch(client,site="https://spys.me/proxy.txt")
        proxies = regex.finditer(proxy_list)
        for i in re.findall(regex,proxy_list):
            try:
                proxy = next(proxies)
            except:
                break
            connector = ProxyConnector(ProxyType.HTTP, host = proxy.group(1), port = proxy.group(2))
            async with aiohttp.ClientSession(connector=connector,cookie_jar=cookie_jar) as client:
                try:
                    data = await fetch(client, site = 'https://google.com')
                    data = await fetch(client, site = 'http://ip-api.com/json/?fields=status,message,country,regionName,city,isp,org,proxy,query')
                    print("\n" + data)
                    print(proxy.group(1))
                    print(proxy.group(2))
                    working_proxies.append(proxy.group(1) + ":" + proxy.group(2))
                    working_proxies_count+=1
                except:
                    continue
    working_current_proxies = await read_proxy_list()
    while True:
        try:
            proxy = next(working_current_proxies)
        except:
            break
        connector = ProxyConnector(ProxyType.HTTP, host = proxy.group(1), port = proxy.group(2))
        async with aiohttp.ClientSession(connector=connector,cookie_jar=cookie_jar) as client:
            try:
                data = await fetch(client, site = 'https://google.com')
                data = await fetch(client, site = 'http://ip-api.com/json/?fields=status,message,country,regionName,city,isp,org,proxy,query')
                print(data)
                print(proxy.group(1))
                print(proxy.group(2))
                working_proxies.append(proxy.group(0))
                working_proxies_count+=1
            except:
                continue
    open("working_proxy_list.txt","w").close()
    with open("working_proxy_list.txt","w") as file:
        for i in range(len(working_proxies)):
            file.write(working_proxies[i] + "\n")
    animasyon = False
    if(working_proxies_count == 0):
        print("\nCouldn't find proxy.")
    else:
        print(working_proxies_count + " proxies written to working_proxy_list.txt")

asyncio.run(main())