import asyncio
import re
import json
from playwright.async_api import async_playwright


async def extraer_audifonos_phonak():
    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=True)
        pagina = await navegador.new_page()

        url_principal = "https://www.phonak.com/es-es/dispositivos-auditivos/audifonos"
        await pagina.goto(url_principal, timeout=60000)

        await pagina.wait_for_selector("a[href*='/es-es/dispositivos-auditivos/audifonos/']", state="attached", timeout=30000)

        enlaces = await pagina.query_selector_all("a[href*='/es-es/dispositivos-auditivos/audifonos/']")
        urls = list({await enlace.get_attribute("href") for enlace in enlaces})
        urls = [u for u in urls if u and u.startswith("/es-es/dispositivos-auditivos/audifonos/")]

        datos = []
        for path in urls:
            url = f"https://www.phonak.com{path}"
            await pagina.goto(url)
            try:
                await pagina.wait_for_selector("h1", timeout=10000)
                nombre = await (await pagina.query_selector("h1")).inner_text()

                datos.append({
                    "modelo": nombre,
                    "url": url
                })
            except Exception as e:
                print(f"Error al scrapear {url}: {e}")

        await navegador.close()
        return datos

if __name__ == "__main__":
    resultados = asyncio.run(extraer_audifonos_phonak())

    with open("audifonos_phonak.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)