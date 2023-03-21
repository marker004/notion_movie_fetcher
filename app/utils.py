from aiohttp import ClientSession
import asyncio


async def async_aiohttp_get_all_text(urls):
    async with ClientSession() as session:

        async def fetch(url):
            async with session.get(url) as response:
                return await response.text()

        return await asyncio.gather(*[fetch(url) for url in urls])


async def async_aiohttp_get_all_json(urls):
    async with ClientSession() as session:

        async def fetch(url):
            async with session.get(url) as response:
                return await response.json(content_type="text/json")

        return await asyncio.gather(*[fetch(url) for url in urls])
