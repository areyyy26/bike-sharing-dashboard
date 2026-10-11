# Bike Sharing Dashboard

Dashboard interaktif untuk analisis data penyewaan sepeda menggunakan Streamlit.

## Struktur yang disarankan

```text
submission/
├── dashboard/
│   ├── dashboard.py
│   └── main_data.csv
├── data/
│   └── hour.csv
├── Proyek_Analisis_Data_Bike_Sharing_Template_Dicoding.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Menjalankan dashboard secara lokal

1. Buka terminal pada folder `submission`.
2. Install dependensi:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Pastikan dataset tersedia di `dashboard/main_data.csv` atau `data/hour.csv`.
4. Jalankan:

   ```bash
   python -m streamlit run dashboard/dashboard.py
   ```

Streamlit akan menampilkan alamat lokal di terminal. Buka alamat tersebut di browser.

## Isi dashboard

- Filter rentang tanggal, musim, dan kondisi cuaca.
- KPI total penyewaan, rata-rata penyewaan per jam, dan jumlah hari.
- Grafik total penyewaan berdasarkan jam, musim, dan cuaca.
- Tabel rata-rata penyewaan per jam serta data terfilter.
