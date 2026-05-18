from PIL import Image
import os

for j in range(104, 110):
    print(f"\nProduto {j}")
    for i in [1,2,3,4]:
        path = f'assets/produto_{j}/foto_{i}.jpg'
        if os.path.exists(path):
            img = Image.open(path).convert('L')
            hist = img.histogram()
            brancos = sum(hist[240:256])
            total = img.width * img.height
            pct = brancos/total * 100
            print(f'foto_{i}: {pct:.1f}% pixels brancos')
