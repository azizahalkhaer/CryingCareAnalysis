import os
from rembg import remove
from PIL import Image

# Daftar nama file yang ingin kita hapus latar belakangnya
target_files = ['logo', 'overview', 'analytic', 'setting']

print("========================================")
print("🪄  MEMULAI PROSES HAPUS BACKGROUND AI")
print("========================================\n")

for name in target_files:
    input_path = None
    
    # Mencari file entah itu berakhiran .jpeg, .jpg, atau .png
    for ext in ['.jpeg', '.jpg', '.png']:
        if os.path.exists(name + ext):
            input_path = name + ext
            break
            
    if input_path:
        output_path = name + '.png' # Paksa simpan jadi .png
        print(f"⏳ Sedang memproses: {input_path} ...")
        
        try:
            # Buka gambar asli
            input_image = Image.open(input_path)
            
            # PROSES SAKTI: Hapus background menggunakan AI
            output_image = remove(input_image)
            
            # Simpan hasil yang sudah transparan
            output_image.save(output_path)
            print(f"   ✅ BERHASIL! Disimpan sebagai: {output_path}\n")
            
        except Exception as e:
            print(f"   ❌ Gagal memproses {input_path}. Error: {e}\n")
    else:
        print(f"   ⚠️ File gambar untuk '{name}' tidak ditemukan di folder ini.\n")

print("🎉 SEMUA PROSES SELESAI!")
print("Sekarang kamu bisa jalankan kembali 'streamlit run app.py'")
print("========================================")