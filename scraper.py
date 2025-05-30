# scraper.py
# Script Python ini akan digunakan untuk scraping data manga dari sumber web.
# Menggunakan requests untuk membuat permintaan HTTP dan BeautifulSoup untuk parsing HTML.

import requests
from bs4 import BeautifulSoup
import json
import time # Untuk menambahkan delay antar permintaan (penting untuk scraping yang bertanggung jawab)

def scrape_manga_list(url):
    """
    Mengikis daftar manga dari URL yang diberikan.
    Ini adalah contoh dasar dan perlu disesuaikan dengan struktur HTML situs target.

    Args:
        url (str): URL halaman yang akan di-scrape.

    Returns:
        list: Daftar kamus, setiap kamus mewakili satu manga.
              Contoh: [{'title': 'Manga Title', 'cover_url': '...', 'genres': [...]}]
    """
    print(f"Memulai scraping dari: {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    manga_data = []

    try:
        response = requests.get(url, headers=headers, timeout=10) # Timeout 10 detik
        response.raise_for_status() # Akan memunculkan HTTPError untuk status kode respons yang buruk (4xx atau 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Contoh: Menemukan elemen yang berisi daftar manga ---
        # Ini adalah bagian yang paling penting dan spesifik situs.
        # Anda perlu menginspeksi elemen HTML dari situs target (misal MangaDex/MyAnimeList)
        # dan menyesuaikan selektor di bawah ini.

        # Contoh placeholder: Mencari semua div dengan kelas 'manga-item'
        # Ganti 'manga-item' dengan kelas atau selektor yang sebenarnya dari situs target Anda.
        manga_items = soup.find_all('div', class_='bsx')

        if not manga_items:
            print("Tidak ada elemen manga ditemukan. Periksa selektor HTML.")
            # Sebagai fallback, coba cari elemen lain yang mungkin berisi data
            # Misalnya, jika situs menggunakan struktur yang berbeda
            # Anda bisa menambahkan logika pencarian alternatif di sini.
            # Untuk tujuan demonstrasi, kita akan menambahkan data dummy jika tidak ada yang ditemukan.
            print("Menambahkan data dummy karena tidak ada elemen yang ditemukan.")
            manga_data.append({
                'title': 'Dummy Manga 1',
                'cover_url': 'https://placehold.co/200x300/333/fff?text=Dummy+Manga+1',
                'rating': 4.5,
                'total_ratings': 100,
                'genres': ['Action', 'Fantasy'],
                'description': 'Ini adalah deskripsi dummy untuk manga 1.',
                'source_url': 'http://example.com/dummy-manga-1'
            })
            manga_data.append({
                'title': 'Dummy Manga 2',
                'cover_url': 'https://placehold.co/200x300/333/fff?text=Dummy+Manga+2',
                'rating': 4.2,
                'total_ratings': 80,
                'genres': ['Romance', 'Comedy'],
                'description': 'Ini adalah deskripsi dummy untuk manga 2.',
                'source_url': 'http://example.com/dummy-manga-2'
            })
            return manga_data


        for item in manga_items:
            title_tag = item.find('div', class_='tt') # Contoh selektor judul
            cover_img = item.find('img', class_='ts-post-image wp-post-image attachment-medium size-medium') # Contoh selektor gambar cover
            description_tags = item.find_all('div', class_='entry-content entry-content-single')
            genre_tags = item.find_all('div', class_='seriestugenre') # Contoh selektor genre

            title = title_tag.get_text(strip=True) if title_tag else 'N/A'
            cover_url = cover_img['src'] if cover_img else 'N/A'
            desk = [d.get_text(strip=True) for d in description_tags]
            genres = [g.get_text(strip=True) for g in genre_tags]

            # TODO: Ekstrak rating, total rating, deskripsi, dll., sesuai kebutuhan
            # Ini akan sangat spesifik pada struktur HTML situs target.

            manga_data.append({
                'title': title,
                'cover_url': cover_url,
                'genres': genres,
                'rating': None, # Placeholder
                'total_ratings': None, # Placeholder
                'description': desk, # Placeholder
                'source_url': url # Atau URL spesifik manga jika tersedia
            })

            # Tambahkan delay untuk menghindari pemblokiran IP
            time.sleep(0.5) # Jeda 0.5 detik antar setiap item (sesuaikan)

    except requests.exceptions.RequestException as e:
        print(f"Error saat melakukan permintaan HTTP: {e}")
    except Exception as e:
        print(f"Terjadi kesalahan saat scraping: {e}")

    return manga_data

def save_to_json(data, filename):
    """Menyimpan data yang di-scrape ke file JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data berhasil disimpan ke {filename}")

def main():
    # Ganti dengan URL situs manga yang ingin Anda scrape
    # Untuk tujuan demonstrasi, saya menggunakan URL placeholder.
    # Anda harus mengganti ini dengan URL MangaDex atau MyAnimeList yang sebenarnya.
    target_url = "https://mangakita.id/manga/?page=2" # Ganti dengan URL yang sebenarnya!

    scraped_data = scrape_manga_list(target_url)

    if scraped_data:
        print(f"\nBerhasil mengikis {len(scraped_data)} item manga.")
        # Simpan data ke file JSON
        save_to_json(scraped_data, 'manga_data.json')
        # Anda juga bisa mengirim data ini ke API backend Anda di sini
        # Contoh:
        # for manga in scraped_data:
        #     requests.post('http://localhost:5000/api/manga', json=manga)
    else:
        print("Tidak ada data manga yang diikis.")

if __name__ == "__main__":
    main()
