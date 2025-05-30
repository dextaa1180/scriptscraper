# scraper.py
# Script Python ini akan digunakan untuk melakukan deep scraping data manga dari https://mangakita.id/
# Mengunjungi halaman daftar, lalu mengunjungi setiap halaman detail manga.

import requests
from bs4 import BeautifulSoup
import json
import time
import re # Untuk regex, jika diperlukan nanti untuk membersihkan teks

# Header untuk permintaan HTTP
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_page_soup(url, timeout=10):
    """Mengambil objek BeautifulSoup dari URL yang diberikan."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status() # Memunculkan HTTPError untuk status kode yang buruk
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error saat mengakses {url}: {e}")
        return None

def scrape_manga_details(detail_url):
    """
    Mengikis detail manga (judul, cover, deskripsi, genre) dari halaman detail manga.
    Menggunakan selektor yang disesuaikan untuk mangakita.id.
    """
    print(f"  Mengikis detail dari: {detail_url}")
    soup = get_page_soup(detail_url)
    if not soup:
        return None

    details = {}

    # Judul Manga (di halaman detail, mungkin berbeda dari halaman daftar)
    title_tag = soup.find('h1', class_='entry-title')
    details['title'] = title_tag.text.strip() if title_tag else 'N/A'

    # Gambar Cover Manga
    cover_img_tag = soup.find('div', class_='thumb')
    if cover_img_tag:
        img_src = cover_img_tag.find('img')
        details['cover_url'] = img_src['src'] if img_src and 'src' in img_src.attrs else 'N/A'
    else:
        details['cover_url'] = 'N/A'

    # Deskripsi
    description_div = soup.find('div', class_='entry-content entry-content-single')
    details['description'] = description_div.text.strip() if description_div else 'N/A'
    # Mungkin perlu membersihkan teks deskripsi dari "Sinopsis" atau label lain

    # Genre
    genres_list = []
    genre_div = soup.find('div', class_='seriestugenre')
    if genre_div:
        genre_links = genre_div.find_all('a')
        genres_list = [link.text.strip() for link in genre_links]
    details['genres'] = genres_list

    # Rating (Opsional, jika ada di halaman detail dan ingin diambil)
    # Anda perlu menginspeksi halaman detail untuk menemukan selektor rating.
    details['rating'] = None # Placeholder
    details['total_ratings'] = None # Placeholder

    time.sleep(0.5) # Jeda setelah scrape detail
    return details

def scrape_manga_list_page(list_url):
    """
    Mengikis URL manga dari halaman daftar.
    Menggunakan selektor yang telah Anda tetapkan untuk mangakita.id.
    """
    print(f"Memproses halaman daftar: {list_url}")
    soup = get_page_soup(list_url)
    if not soup:
        return []

    manga_urls = []
    # Selektor untuk item manga di halaman daftar
    manga_items = soup.find_all('div', class_='bsx')

    if not manga_items:
        print("Tidak ada elemen manga ditemukan dengan selektor 'bsx' di halaman daftar ini.")
        return []

    for item in manga_items:
        link_tag = item.find('a') # Link ke halaman detail manga ada di tag 'a'
        if link_tag and 'href' in link_tag.attrs:
            manga_urls.append(link_tag['href'])
    
    return manga_urls

def save_to_json(data, filename):
    """Menyimpan data yang di-scrape ke file JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data berhasil disimpan ke {filename}")

def main():
    base_list_url = "https://mangakita.id/manga/"
    page_number = 1
    all_manga_details = []
    output_filename = 'all_manga_details.json' # Nama file output JSON

    while True:
        if page_number == 1:
            current_list_url = base_list_url
        else:
            current_list_url = f"{base_list_url}?page={page_number}"

        print(f"\n--- Mengikis Halaman Daftar: {current_list_url} ---")
        
        # Mendapatkan daftar URL manga dari halaman daftar saat ini
        manga_urls_on_page = scrape_manga_list_page(current_list_url)

        if not manga_urls_on_page:
            print(f"Tidak ada URL manga yang ditemukan di halaman daftar {current_list_url}. Menghentikan looping.")
            break # Hentikan jika tidak ada URL manga di halaman daftar

        # Melakukan deep scraping untuk setiap URL manga yang ditemukan di halaman ini
        for manga_url in manga_urls_on_page:
            details = scrape_manga_details(manga_url)
            if details:
                all_manga_details.append(details)
                # Simpan data ke JSON setelah setiap manga di-scrape
                save_to_json(all_manga_details, output_filename)
            time.sleep(0.5) # Jeda setelah scrape detail manga

        page_number += 1
        time.sleep(1) # Jeda lebih lama antar halaman daftar

    print(f"\n===== Proses Deep Scraping Selesai =====")
    print(f"Total {len(all_manga_details)} item manga berhasil dikumpulkan dan disimpan ke {output_filename}.")

if __name__ == "__main__":
    main()