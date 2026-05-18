import requests, re
html = requests.get('https://www.bobswatches.com/').text
videos = re.findall(r'https://[^\"\'\s]+\.mp4', html)
print(set(videos))
