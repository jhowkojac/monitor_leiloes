import httpx
from bs4 import BeautifulSoup

try:
    response = httpx.get('https://leilao.detran.mg.gov.br/', timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Procura por todos os links
    all_links = soup.find_all('a', href=True)
    print(f'Total de links: {len(all_links)}')
    
    # Mostra todos os textos de links
    for i, link in enumerate(all_links[:20]):
        text = link.get_text().strip()
        href = link.get('href')
        print(f'{i+1}. Texto: "{text}"')
        print(f'   Href: {href}')
        print()
    
    # Procura por qualquer elemento que tenha "leilão" ou "edital"
    leiloes_elements = soup.find_all(string=lambda text: text and any(word in text.lower() for word in ['leilão', 'edital', 'detalhe']))
    print(f'Elementos com leilão/edital: {len(leiloes_elements)}')
    
    for i, element in enumerate(leiloes_elements[:10]):
        print(f'{i+1}. Texto: "{element.strip()}"')
    
except Exception as e:
    print(f'Erro: {e}')
