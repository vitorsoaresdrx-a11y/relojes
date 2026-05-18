import asyncio
import json
import os
import requests
from playwright.async_api import async_playwright

BASE_URL = "https://www.bobswatches.com"
CATALOG_URL = "https://www.bobswatches.com/cartier/"
OUTPUT_JSON = "products.json"
ASSETS_DIR = "assets"

os.makedirs(ASSETS_DIR, exist_ok=True)

async def baixar_imagem(url, path):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": BASE_URL
        }
        full_url = url if url.startswith("http") else f"{BASE_URL}{url}"
        r = requests.get(full_url, headers=headers, timeout=10)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            return True
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")
    return False

async def scrape_produto(page, url, produto_id):
    try:
        for tentativa in range(3):
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=90000)
                break
            except:
                if tentativa == 2:
                    print(f"Falhou 3x: {url}")
                    return None
                await asyncio.sleep(3)

        await page.wait_for_timeout(5000)

        try:
            await page.locator("text=Got it!").click(timeout=3000)
        except:
            pass

        # Título
        title_el = await page.query_selector("h1")
        title = await title_el.inner_text() if title_el else "Sem título"

        # Preço
        price_el = await page.query_selector(".price, .item-price, .product-price, [class*='price']")
        price = await price_el.inner_text() if price_el else "Sob consulta"

        # Referência
        import re
        ref_match = re.search(r'\b\d{4,6}[A-Za-z0-9\-]*\b', title)
        referencia = ref_match.group(0) if ref_match else "N/A"

        # Specs
        specs = {}
        rows = await page.query_selector_all("tr")
        for row in rows:
            try:
                tds = await row.query_selector_all("td")
                if len(tds) == 2:
                    key = (await tds[0].inner_text()).strip().lower()
                    val = (await tds[1].inner_text()).strip()
                    if val:
                        specs[key] = val
            except:
                continue

        # Fotos
        pasta_produto = os.path.join(ASSETS_DIR, f"produto_{produto_id}")
        os.makedirs(pasta_produto, exist_ok=True)
        fotos_locais = []
        fotos_vistas = set()

        # 1. Encontrar o SKU do produto para garantir que pegamos as fotos exatas
        sku = None
        import re
        
        # Procura SKU no texto da página
        try:
            texto_pagina = await page.inner_text("body")
            match_sku = re.search(r'Item No\.\s*(\d{5,7})', texto_pagina)
            if match_sku:
                sku = match_sku.group(1)
        except:
            pass

        # Se não achou no texto, procura no src de alguma imagem principal
        if not sku:
            todas = await page.query_selector_all("img")
            for img in todas:
                src = await img.get_attribute("src") or ""
                match_img = re.search(r'SKU(\d{5,7})', src, re.IGNORECASE)
                if match_img:
                    sku = match_img.group(1)
                    break
                    
        print(f"  SKU Encontrado: {sku}")

        # 2. Extrair TODAS as imagens que pertençam a esse SKU
        todas_imgs = await page.query_selector_all("img")
        for img in todas_imgs:
            src = await img.get_attribute("src") or await img.get_attribute("data-src") or ""
            if not src:
                continue
                
            is_valid = False
            # O melhor critério: a imagem tem o SKU do produto!
            if sku and f"sku{sku}" in src.lower():
                is_valid = True
            # Fallback se não descobrir o SKU
            elif not sku and ("cartier" in src.lower() or "used" in src.lower()):
                if not any(x in src.lower() for x in ["logo", "icon", "carousel", "banner", "trending", "similar"]):
                    is_valid = True
                    
            if is_valid:
                full_url = src if src.startswith("http") else f"{BASE_URL}{src}"
                # Tenta pegar em alta resolução modificando a URL do CDN do Bob's Watches
                alta_res = re.sub(r'width=\d+', 'width=1000', full_url)
                
                if alta_res not in fotos_vistas:
                    fotos_vistas.add(alta_res)
                    nome_arquivo = f"foto_{len(fotos_locais) + 1}.jpg"
                    caminho_local = os.path.join(pasta_produto, nome_arquivo)
                    
                    ok = await baixar_imagem(alta_res, caminho_local)
                    if ok:
                        fotos_locais.append(f"./{caminho_local}")
                        print(f"  Foto {len(fotos_locais)} baixada: {alta_res.split('/')[-1][:20]}...")

        print(f"Produto {produto_id}: {title.strip()} — {len(fotos_locais)} fotos")

        return {
            "id": produto_id,
            "titulo": title.strip(),
            "referencia": referencia,
            "preco": price.strip(),
            "url": url,
            "fotos": fotos_locais,
            "specs": specs
        }

    except Exception as e:
        print(f"Erro no produto {url}: {e}")
        return None

async def scrape_catalogo():
    print("Iniciando scraper...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print(f"Acessando catálogo: {CATALOG_URL}")
        await page.goto(CATALOG_URL, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)

        try:
            await page.keyboard.press("Escape")
        except:
            pass

        # Scroll mais agressivo pra carregar todos os produtos
        print("Carregando produtos via scroll...")
        ultima_altura = 0
        for i in range(30):
            await page.evaluate("window.scrollBy(0, 2000)")
            await page.wait_for_timeout(1500)
            altura_atual = await page.evaluate("document.body.scrollHeight")
            if altura_atual == ultima_altura:
                print(f"Scroll parado no ciclo {i+1} — página totalmente carregada.")
                break
            ultima_altura = altura_atual

        # Coleta links — aceita qualquer link de produto da URL base
        links_els = await page.query_selector_all("a[href*='.html']")
        links_validos = []
        vistos = set()

        # Palavras que indicam página genérica, não produto
        IGNORAR = [
            "#", "javascript", "contact", "sell", "about", "blog",
            "luxury-watches", "sitemap", "privacy", "terms"
        ]

        for el in links_els:
            href = await el.get_attribute("href")
            if not href:
                continue
            full = href if href.startswith("http") else f"{BASE_URL}{href}"
            if full in vistos:
                continue
            # Produtos terminam em .html
            if not full.endswith(".html"):
                continue
            # Ignora páginas institucionais
            if any(x in full.lower() for x in IGNORAR):
                continue
            # Garante que é da marca atual ou genérico "used-"
            marca_atual = CATALOG_URL.rstrip('/').split('/')[-1].lower()
            if marca_atual not in full.lower() and "used" not in full.lower():
                continue
                
            vistos.add(full)
            links_validos.append(full)

        print(f"{len(links_validos)} produtos encontrados.")

        # Carrega o JSON antes para saber o ID inicial e não sobrescrever pastas de imagens
        todos_produtos = []
        if os.path.exists(OUTPUT_JSON):
            try:
                with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
                    dados_antigos = json.load(f)
                    todos_produtos = dados_antigos.get("products", [])
                print(f"Carregado catálogo anterior com {len(todos_produtos)} produtos.")
            except Exception as e:
                print(f"⚠️ Erro ao ler {OUTPUT_JSON} (ele pode estar corrompido): {e}")
                print("Iniciando catálogo do zero!")
                
        start_id = len(todos_produtos)

        products_data = []
        for i, link in enumerate(links_validos):
            print(f"\n[{i+1}/{len(links_validos)}] {link}")
            novo_id = start_id + i + 1
            produto = await scrape_produto(page, link, novo_id)
            if produto:
                products_data.append(produto)
                todos_produtos.append(produto)
                
                # Salva a cada produto novo para não perder dados se o script for cancelado
                with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
                    json.dump({"products": todos_produtos}, f, indent=2, ensure_ascii=False)
                    
            await page.wait_for_timeout(2000)

        await browser.close()

        print(f"\nConcluído! {len(products_data)} novos produtos adicionados.")
        print(f"Total no catálogo agora: {len(todos_produtos)} produtos em {OUTPUT_JSON}")

if __name__ == "__main__":
    asyncio.run(scrape_catalogo())