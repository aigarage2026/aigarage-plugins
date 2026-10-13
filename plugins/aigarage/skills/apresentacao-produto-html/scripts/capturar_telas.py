"""Captura screenshots das rotas de um app local para a apresentação.
Uso: python capturar_telas.py http://localhost:3000 /dashboard /pedidos /relatorios
Requer: pip install playwright && playwright install chromium
Saída: ./telas/<rota>.jpg  (1440x900, JPEG q82)
"""
import sys, asyncio, pathlib
from playwright.async_api import async_playwright

async def main(base, rotas):
    pathlib.Path("telas").mkdir(exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1440, "height": 900})
        for r in rotas:
            await pg.goto(base.rstrip("/") + r, wait_until="networkidle")
            await pg.wait_for_timeout(800)
            nome = r.strip("/").replace("/", "_") or "home"
            await pg.screenshot(path=f"telas/{nome}.jpg", type="jpeg", quality=82)
            print("ok", nome)
        await b.close()

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2:]))
