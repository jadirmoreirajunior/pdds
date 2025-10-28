# Arquivo: clipping_scraper.py
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

# 1. Configurações
SOURCES = [
    {"name": "SEMAD", "url": "https://semad.mg.gov.br/noticias"},
    {"name": "IEF", "url": "https://ief.mg.gov.br/noticias"},
    {"name": "FEAM", "url": "https://feam.br/noticias"},
    {"name": "IGAM", "url": "https://igam.mg.gov.br/noticias"}
]

# Seletor final (o mais provável para Liferay): procura links <a> dentro de listas de ativos
# Se o site fosse estático, este seletor funcionaria sem proxy
SELECTOR = 'div.asset-full-content a, ul.asset-full-content a, .asset-list a'

# 2. Funções de Scraping
def scrape_news():
    """Busca as notícias das fontes do Sisema."""
    all_extracted_news = []
    
    for source in SOURCES:
        try:
            # Não precisa de proxy. O Requests faz a chamada direta.
            response = requests.get(source['url'], timeout=15)
            response.raise_for_status() # Lança erro para status ruins (4xx ou 5xx)
            
            # Analisa o HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Encontra os elementos de notícia com o seletor
            news_elements = soup.select(SELECTOR)
            
            # Pega as 5 primeiras notícias de cada órgão
            for element in news_elements[:5]:
                title = element.text.strip()
                link = element.get('href')
                
                if title and link:
                    # Trata links relativos (transforma /noticia/detalhe em URL completa)
                    if not link.startswith('http'):
                        base_url = requests.compat.urlparse(source['url']).scheme + '://' + requests.compat.urlparse(source['url']).netloc
                        link = base_url + link
                    
                    all_extracted_news.append({
                        "source": source['name'],
                        "title": title,
                        "link": link
                    })
                    
        except requests.exceptions.RequestException as e:
            print(f"Falha ao buscar notícias em {source['name']}: {e}")
            all_extracted_news.append({
                "source": source['name'],
                "title": f"*-- Falha na {source['name']}. Erro de conexão/estrutura. --*",
                "link": ""
            })

    return all_extracted_news

# 3. Função Principal
def main():
    extracted_news = scrape_news()
    
    # Formata o resultado para um arquivo de texto simples (mais fácil de ler)
    output_lines = []
    
    if extracted_news:
        for item in extracted_news:
            # Adiciona o nome do órgão no título para identificação
            title = f"[{item['source']}] {item['title']}" if item['link'] else item['title']
            
            output_lines.append(title)
            if item['link']:
                output_lines.append(item['link'])
            
    # Cria o conteúdo final do arquivo
    output_content = "\n".join(output_lines).strip()
    
    # Salva o resultado no seu repositório como um arquivo TXT
    # O GitHub Actions tem permissão para fazer isso.
    with open('clipping_raw_output.txt', 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print("Dados extraídos e salvos em 'clipping_raw_output.txt'")

if __name__ == "__main__":
    main()
