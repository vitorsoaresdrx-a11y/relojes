import os
import shutil
import re

ASSETS_DIR = r"C:\Users\Arabe\Documents\relogios\assets"

for filename in os.listdir(ASSETS_DIR):
    filepath = os.path.join(ASSETS_DIR, filename)
    
    if not os.path.isfile(filepath):
        continue
    
    # Pega o número do produto do nome do arquivo ex: produto_1_foto_1.jpg
    match = re.search(r'produto_(\d+)', filename)
    if not match:
        continue
    
    produto_id = match.group(1)
    pasta_destino = os.path.join(ASSETS_DIR, f"produto_{produto_id}")
    os.makedirs(pasta_destino, exist_ok=True)
    
    shutil.move(filepath, os.path.join(pasta_destino, filename))
    print(f"Movido: {filename} → produto_{produto_id}/")

print("Concluído!")