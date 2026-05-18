import json
import os

CHAVES_IGNORAR = {
    "bigger text", "bigger cursor", "color adjustments", "grayscale mode",
    "hide images", "reading line", "reading mask", "readable fonts",
    "highlight links", "dyslexic fonts", "page structure", "keyboard navigation",
    "alt text for images", "read page aloud", "stop animations"
}

def limpar_specs(specs_raw):
    specs_limpas = {}
    for key, val in specs_raw.items():
        if key.lower() in CHAVES_IGNORAR:
            continue
        specs_limpas[key] = val
    return specs_limpas

def normalizar_caminho(caminho):
    return caminho.replace("\\", "/").replace("./", "")

def merge_data():
    try:
        with open('products.json', 'r', encoding='utf-8') as f:
            bobs_data = json.load(f)
    except FileNotFoundError:
        print("Arquivo products.json não encontrado.")
        return

    PRECOS_INVALIDOS = {"Min", "", "Sob consulta"}

    new_watches = []
    for item in bobs_data.get('products', []):
        # Gera preço aleatório entre 159 e 550 reais, conforme solicitado
        import random
        preco_num = random.randint(159, 550)
        preco = f"R$ {preco_num},00"

        fotos = item.get('fotos', [])
        if not fotos:
            print(f"Produto sem fotos pulado: {item.get('titulo')}")
            continue

        images = [normalizar_caminho(f) for f in fotos if f]
        
        # Inteligência Artificial básica para achar a foto de estúdio (fundo branco):
        # A foto com fundo branco terá uma claridade (luminância) média muito maior que uma foto de pulso/madeira.
        if len(images) > 1:
            try:
                from PIL import Image, ImageChops
                
                melhor_idx = 0
                maior_ratio = -1
                
                # Procura em todas as fotos a que tem o formato mais "esticado para cima" (maior h/w)
                # Relógios de frente sempre têm altura > largura (pulseira em cima/baixo).
                # Relógios de lado ficam mais "quadrados" ou largos.
                for idx in range(len(images)):
                    path = images[idx].replace('./', '')
                    with Image.open(path) as img:
                        gray = img.convert('L')
                        # Conta pixels quase brancos para confirmar se é foto de estúdio
                        hist = gray.histogram()
                        brancos = sum(hist[240:256])
                        total = gray.width * gray.height
                        pct_branco = (brancos / total) * 100
                        
                        # Se tiver mais de 20% de branco, é foto de estúdio
                        if pct_branco > 20:
                            bg = Image.new('L', img.size, 255)
                            diff = ImageChops.difference(gray, bg)
                            diff = diff.point(lambda p: p > 10 and 255)
                            bbox = diff.getbbox()
                            if bbox:
                                w = bbox[2] - bbox[0]
                                h = bbox[3] - bbox[1]
                                ratio = h / w if w > 0 else 0
                                
                                if ratio > maior_ratio:
                                    maior_ratio = ratio
                                    melhor_idx = idx
                
                # Coloca a foto de frente como a principal (capa)
                if melhor_idx != 0 and maior_ratio > 0:
                    foto_frente = images.pop(melhor_idx)
                    images.insert(0, foto_frente)
            except Exception as e:
                print(f"Erro na analise de imagem: {e}")

        if not images:
            print(f"Produto sem fotos validas: {item.get('titulo')}")
            continue

        title = item.get('titulo', 'Sem título')
        title_lower = title.lower()

        KNOWN_BRANDS = [
            "Patek Philippe", "Rolex", "Richard Mille", "Audemars Piguet", "Omega",
            "Cartier", "Tissot", "Breitling", "Hublot", "TAG Heuer", "Panerai", "IWC",
            "Tudor", "Seiko", "Grand Seiko", "Jaeger-LeCoultre", "Vacheron Constantin",
            "Chopard", "Blancpain", "Breguet", "Bulgari", "Zenith"
        ]
        
        brand = "Outros"
        for b in KNOWN_BRANDS:
            if b.lower() in title_lower:
                brand = b
                break
                
        if brand == "Outros":
            # Se não achar na lista, usa a primeira palavra do título como marca
            clean_title = title.replace("Used ", "").replace("Pre-Owned ", "").replace("Vintage ", "").strip()
            if clean_title:
                brand = clean_title.split()[0]

        specs_raw = item.get('specs', {})
        specs = limpar_specs(specs_raw)

        watch = {
            "id": item.get('id'),
            "model": title.replace("Used ", "").replace("Pre-Owned ", ""),
            "price": preco,
            "images": images,
            "cover": images[0],
            "brand": brand,
            "url": item.get('url', ''),
            "referencia": item.get('referencia', 'N/A'),
            "specifications": specs if specs else {
                "Movement": "Automatic",
                "Condition": "Pre-Owned"
            }
        }
        new_watches.append(watch)

    output_path = 'bobs_data.js'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("window.bobsWatches = " + json.dumps(new_watches, indent=2, ensure_ascii=False) + ";")

    print(f"Concluído! {len(new_watches)} produtos salvos em {output_path}")

if __name__ == "__main__":
    merge_data()