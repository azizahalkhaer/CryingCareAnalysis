import os
import librosa
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from tqdm import tqdm # Untuk menampilkan progress bar

# 1. Konfigurasi Path
DATASET_PATH = "dataset" # Nama folder dataset kamu

def extract_features(file_path):
    """Fungsi untuk mengambil ciri khas (fitur) dari audio"""
    try:
        # Load audio (sr=22050 adalah standar)
        audio, sample_rate = librosa.load(file_path, res_type='kaiser_fast') 
        # Ekstrak MFCC
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        # Ambil nilai rata-rata dari setiap fitur
        mfccs_scaled = np.mean(mfccs.T, axis=0)
        return mfccs_scaled
    except Exception as e:
        print(f"Error memproses {file_path}: {e}")
        return None

# 2. Proses Membaca Data
X = [] # Untuk menyimpan fitur audio
y = [] # Untuk menyimpan label (kategori)

print("Mulai memproses dataset audio...")
# Loop ke setiap sub-folder di dalam folder dataset
for folder_name in os.listdir(DATASET_PATH):
    folder_path = os.path.join(DATASET_PATH, folder_name)
    
    # Pastikan itu adalah folder (bukan file tersembunyi)
    if os.path.isdir(folder_path):
        print(f"Memproses kategori: {folder_name}")
        
        # Baca semua file di dalam folder tersebut
        for file_name in tqdm(os.listdir(folder_path)):
            if file_name.endswith('.wav') or file_name.endswith('.mp3'):
                file_path = os.path.join(folder_path, file_name)
                
                # Ekstrak fitur
                features = extract_features(file_path)
                if features is not None:
                    X.append(features)
                    y.append(folder_name) # Labelnya adalah nama folder

X = np.array(X)
y = np.array(y)

# 3. Ubah Label teks menjadi angka (Label Encoding)
print("\nMengubah label menjadi angka...")
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

# 4. Bagi data menjadi Data Latih (80%) dan Data Uji (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# 5. Latih Model (Menggunakan Random Forest)
print("Sedang melatih model Machine Learning...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 6. Cek Akurasi
y_pred = model.predict(X_test)
akurasi = accuracy_score(y_test, y_pred)
print(f"Selesai! Akurasi Model: {akurasi * 100:.2f}%")

# 7. Simpan Model dan Encoder agar bisa dipakai di Streamlit
joblib.dump(model, 'model_bayi.pkl')
joblib.dump(encoder, 'label_encoder.pkl')
print("Model berhasil disimpan sebagai 'model_bayi.pkl' dan 'label_encoder.pkl'")