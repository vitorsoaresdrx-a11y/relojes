from PIL import Image, ImageChops
import os

for j in [104, 105, 106, 107, 108, 209]:
    print(f"\nProduto {j}")
    for i in [1,2,3,4,5]:
        path = f'assets/produto_{j}/foto_{i}.jpg'
        if os.path.exists(path):
            img = Image.open(path).convert('L')
            
            hist = img.histogram()
            brancos = sum(hist[240:256])
            total = img.width * img.height
            pct_branco = (brancos / total) * 100
            
            if pct_branco > 20:
                bg = Image.new('L', img.size, 255)
                diff = ImageChops.difference(img, bg)
                diff = diff.point(lambda p: p > 10 and 255)
                bbox = diff.getbbox()
                if bbox:
                    w = bbox[2] - bbox[0]
                    h = bbox[3] - bbox[1]
                    ratio = h / w if w > 0 else 0
                    print(f'foto_{i}: studio ({pct_branco:.1f}% branco), ratio={ratio:.2f}')
            else:
                print(f'foto_{i}: lifestyle ({pct_branco:.1f}% branco)')
