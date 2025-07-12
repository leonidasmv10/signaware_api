import asyncio
from playwright.async_api import async_playwright

async def extraer_todo_texto_visible(url: str):
    async with async_playwright() as p:
        navegador = await p.chromium.launch(headless=True)
        pagina = await navegador.new_page()
        await pagina.goto(url, timeout=60000)
        
        await asyncio.sleep(3)

        texto_total = await pagina.evaluate("""
            () => {
                function esVisible(elemento) {
                    const estilo = window.getComputedStyle(elemento);
                    return estilo &&
                           estilo.visibility !== 'hidden' &&
                           estilo.display !== 'none' &&
                           elemento.offsetHeight > 0 &&
                           elemento.offsetWidth > 0;
                }

                const excluir = ['HEADER', 'NAV', 'FOOTER', 'SCRIPT', 'STYLE'];
                const texto = new Set();
                const nodos = document.body.querySelectorAll('*');

                nodos.forEach(nodo => {
                    if (
                        esVisible(nodo) &&
                        !excluir.includes(nodo.tagName) &&
                        !nodo.closest('header, nav, footer')
                    ) {
                        const contenido = nodo.innerText || nodo.textContent;
                        if (contenido) {
                            const limpio = contenido.trim();
                            if (limpio.length > 20) {
                                texto.add(limpio);
                            }
                        }
                    }
                });

                return Array.from(texto).join('\\n\\n');
            }
        """)

        await navegador.close()
        return texto_total

def guardar_en_txt(texto: str, nombre_archivo="pagina_completa.txt"):
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(texto)

if __name__ == "__main__":
    url = "https://www.phonak.com/es-es/dispositivos-auditivos/audifonos/virto-infinio"
    texto = asyncio.run(extraer_todo_texto_visible(url))
    guardar_en_txt(texto)
    print("Texto visible extraído y guardado en pagina_completa.txt")
