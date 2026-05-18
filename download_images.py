import requests
import os

def test_download():
    url = "https://www.bobswatches.com/cdn-cgi/image/width=768,quality=85,sharpen=0.5/images/zUsed-Rolex-Sky-Dweller-336934-Mint-Green-Dial-SKU186472s.jpg"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bobswatches.com/"
    }
    
    os.makedirs('assets', exist_ok=True)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            with open('assets/test_bobs.jpg', 'wb') as f:
                f.write(response.content)
            print("Sucesso! Imagem salva em assets/test_bobs.jpg")
            print(f"Tamanho do arquivo: {len(response.content)} bytes")
        else:
            print(f"Erro no download. Status code: {response.status_code}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_download()
