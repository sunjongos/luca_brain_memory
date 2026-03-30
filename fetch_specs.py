import requests
from bs4 import BeautifulSoup
import json
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

urls = [
    'https://compuzone.co.kr/product/product_detail.htm?ProductNo=1297948&opt_chk=Y',
    'https://compuzone.co.kr/product/product_detail.htm?ProductNo=1321395&opt_chk=Y',
    'https://compuzone.co.kr/product/product_detail.htm?ProductNo=1309944&opt_chk=Y'
]

results = []
for idx, url in enumerate(urls, 1):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract title
        title_elem = soup.select_one('title')
        title = title_elem.text.strip() if title_elem else 'Unknown Title'
        
        # Compuzone usually has spec tables or specific elements we can grab
        # Let's try to extract any text that looks like PC specs (CPU, RAM, VGA, SSD, etc)
        specs_container = soup.select_one('.product_detail_tab, .detail_info_wrap')
        specs_text = specs_container.text.strip()[:1000] if specs_container else 'Could not find details block'
        
        # Also let's try to find price
        price_elem = soup.select_one('.PrPrice') or soup.select_one('.price_num')
        price = price_elem.text.strip() if price_elem else 'Unknown Price'
        
        results.append({
            'id': idx,
            'url': url,
            'title': title,
            'price': price,
            'extracted_info': specs_text
        })
    except Exception as e:
        results.append({'id': idx, 'url': url, 'error': str(e)})

print(json.dumps(results, ensure_ascii=False, indent=2))
