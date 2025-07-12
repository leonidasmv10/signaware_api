import asyncio
from playwright.async_api import async_playwright

async def extraer_imagenes(url: str):
    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=True)
        pagina = await navegador.new_page()
        await pagina.goto(url, timeout=60000)

        # Esperar a que cargue el contenido
        await asyncio.sleep(3)

        # Extraer URLs de imágenes visibles
        imagenes = await pagina.evaluate("""
            () => {
                function esVisible(elemento) {
                    const style = window.getComputedStyle(elemento);
                    return style && style.visibility !== 'hidden' && style.display !== 'none' && elemento.offsetHeight > 0 && elemento.offsetWidth > 0;
                }
                const imgs = Array.from(document.images);
                return imgs.filter(img => esVisible(img)).map(img => img.src);
            }
        """)

        await navegador.close()
        return imagenes

if __name__ == "__main__":
    url = "https://www.phonak.com/es-es/dispositivos-auditivos/audifonos/virto-infinio"
    imagenes = asyncio.run(extraer_imagenes(url))
    for i, img_url in enumerate(imagenes, 1):
        print(f"{i}: {img_url}")
