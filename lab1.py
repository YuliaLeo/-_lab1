import aiohttp
import asyncio
import os
import urllib.parse
import argparse

async def downloadFile(url, outputFile, progress):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                print(f"Не удалось скачать файл: {response.status} {response.reason}")
                return
            
            totalBytes = 0
            with open(outputFile, "wb") as file:
                async for chunk in response.content.iter_chunked(1024):
                    file.write(chunk)
                    totalBytes += len(chunk)
                    progress["bytes"] = totalBytes

async def progressReporter(progress):
    while not progress["done"]:
        print(f"Скачано: {progress['bytes']} байт")
        await asyncio.sleep(1)

async def main():
    parser = argparse.ArgumentParser(description="Скачивание файла по URL.")
    parser.add_argument("url", type=str, help="URL файла, который нужно скачать.")
    
    args = parser.parse_args()
    url = args.url.strip()
    parsedUrl = urllib.parse.urlparse(url)
    filename = os.path.basename(parsedUrl.path)

    if not filename:
        print("Невозможно определить имя файла из URL.")
        return

    progress = {"bytes": 0, "done": False}

    progressTask = asyncio.create_task(progressReporter(progress))

    try:
        print(f"Загрузка начата")
        await downloadFile(url, filename, progress)
        print(f"Загрузка завершена")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        progress["done"] = True
        await progressTask

if __name__ == "__main__":
    asyncio.run(main())
