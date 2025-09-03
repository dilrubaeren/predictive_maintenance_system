# Predictive Maintenance System  

Bu proje, **makinelerin arıza verme olasılığını tahmin etmek** için geliştirilmiş bir masaüstü uygulamasıdır.  
Uygulama, işlenen sensör verilerini kullanarak farklı makine öğrenmesi modelleri (SVM, Random Forest, XGBoost) ile tahmin yapar ve kullanıcıya risk raporları sunar.  

---

## 🚀 Özellikler  

- **Makine Listesi**: Sağ panelden makineler listelenir, seçilen makinenin özellikleri görüntülenir.  
- **Model Seçimi**: Kullanıcı önceden eğitilmiş modellerden (SVM, Random Forest, XGBoost) birini seçerek tahmin yapabilir.  
- **Tahmin Sonucu**: Seçilen makinenin arıza ihtimali ve risk seviyesi (🔴 Yüksek, 🟡 Orta, 🟢 Düşük) gösterilir.  
- **Yüksek Riskli Makineler**: Seçilen modele göre en yüksek arıza riskine sahip **40 makine** listelenir (sayfa geçişi ile 1–20 ve 21–40).  
- **Raporlama**: Yüksek riskli makineler CSV formatında dışa aktarılabilir.  
- **Makine Profilleri**: Her makinenin özellikleri JSON dosyalarında saklanır ve güncellenebilir.  

---

## 📊 Veri Seti  

Proje, UCI Machine Learning Repository’de bulunan **AI4I 2020 Predictive Maintenance Dataset** veri setini kullanır.  

🔗 [AI4I 2020 Dataset](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset)  

---

## 🛠 Kullanılan Teknolojiler  

- **Python 3.x**  
- **Pandas, NumPy** – Veri işleme  
- **scikit-learn** – Modelleme (SVM, Random Forest)  
- **XGBoost** – Gelişmiş sınıflandırıcı  
- **imblearn (SMOTE)** – Dengesiz veri seti için örnekleme  
- **Joblib** – Model kaydetme/yükleme  
- **Tkinter** – Masaüstü GUI  

---

## 📂 Proje Yapısı  

```
├── data/                          # Veri seti ve işlenmiş veriler
│   ├── ai4i2020.csv
│   └── processed_data.csv
├── machine_profiles/               # JSON formatında makine profilleri
├── models/
│   └── trained_models/
│       └── classification/        # Kaydedilen modeller (.joblib)
├── src/
│   ├── machine_profile.py          # Makine sınıfı
│   ├── machine_manager.py          # Makine yöneticisi
│   ├── data_processor.py           # Veri işleme
│   ├── model_trainer.py            # Model eğitimi
│   └── app_interface.py            # Tkinter GUI
├── main.py                         # Giriş noktası (çalıştırma)
└── README.md
```

---

## ⚙️ Kurulum  

```bash
# Depoyu klonla
git clone https://github.com/kullaniciadi/predictive-maintenance.git
cd predictive-maintenance

# Sanal ortam oluştur ve aktif et (önerilir)
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

# Gerekli kütüphaneleri yükle
pip install -r requirements.txt
```

> `requirements.txt` içine kullanılacak kütüphaneler:  
```txt
pandas
numpy
scikit-learn
xgboost
imbalanced-learn
joblib
```

---

## ▶️ Kullanım  

```bash
python main.py
```

- Program açıldığında veri seti işlenir, modeller eğitilir ve GUI başlatılır.  
- GUI üzerinden makine seçilip model belirlenerek tahmin yapılabilir.  
- Raporlama özelliği ile riskli makineler CSV formatında dışa aktarılabilir.  

---

## 📸 Ekran Görselleri  

_(Buraya GUI ekran görüntülerini ekleyebilirsin)_  

---

## 🔮 Gelecek Çalışmalar  

- Daha fazla makine öğrenmesi algoritmasının eklenmesi (LightGBM, CatBoost).  
- Web tabanlı arayüz geliştirme (Flask/Django/Streamlit).  
- Gerçek zamanlı veri akışı entegrasyonu (IoT cihazları üzerinden).  

---

## 📜 Lisans  

Bu proje yalnızca eğitim amaçlıdır.  
