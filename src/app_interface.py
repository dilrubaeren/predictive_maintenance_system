import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import joblib
import pandas as pd
from datetime import datetime
from src.machine_manager import MachineManager


class PredictiveMaintenanceApp:
    def __init__(self, root):
        self.root = root
        self.manager = MachineManager()  # Makine yöneticisi
        self.loaded_model = None  # Yüklü model
        self.selected_machine_id = None  # Seçili makine ID
        self.current_risk_page = 0  # Risk listesi sayfa numarası (0: 1-20, 1: 21-40)
        self.setup_ui()  # Arayüzü kur
        self.refresh_high_risk_list()  # Risk listesini güncelle

    def setup_ui(self):
        """Arayüz bileşenlerini oluşturur."""
        self.root.title("Predictive Maintenance System")
        self.root.geometry("900x650")

        # Ana çerçeveler
        self.create_left_panel()  # Sol panel - Makine listesi
        self.create_middle_panel()  # Orta panel - Makine detayları
        self.create_right_panel()  # Sağ panel - Model tahminleri
        self.create_bottom_panel()  # Alt panel - Risk listesi ve raporlama

    def create_left_panel(self):
        """Sol panel: Makine listesi ve arama kutusu."""
        left_frame = ttk.Frame(self.root, width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Başlık
        ttk.Label(left_frame, text="Makine Listesi", font=('Helvetica', 12, 'bold')).pack(pady=5)

        # Arama kutusu
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(search_frame, text="Ara:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", self.filter_machines)

        # Makine listesi
        self.machine_listbox = tk.Listbox(left_frame, width=25, height=25)
        self.machine_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.refresh_machine_list()
        self.machine_listbox.bind("<<ListboxSelect>>", self.on_machine_select)

    def create_middle_panel(self):
        """Orta panel: Seçili makinenin detayları."""
        middle_frame = ttk.Frame(self.root)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(middle_frame, text="Makine Detayları", font=('Helvetica', 12, 'bold')).pack(pady=5)

        self.detail_text = tk.Text(middle_frame, wrap=tk.WORD, height=10, state=tk.DISABLED)
        self.detail_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Özellik güncelleme butonu
        ttk.Button(middle_frame, text="Özellikleri Güncelle", command=self.update_machine_features).pack(pady=5)

    def create_right_panel(self):
        """Sağ panel: Model seçimi ve tahmin butonu."""
        right_frame = ttk.Frame(self.root, width=200)
        right_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        ttk.Label(right_frame, text="Model Tahmini", font=('Helvetica', 12, 'bold')).pack(pady=5)

        # Model seçim combobox
        ttk.Label(right_frame, text="Model:").pack(anchor=tk.W)
        self.model_var = tk.StringVar()
        self.model_combobox = ttk.Combobox(
            right_frame,
            textvariable=self.model_var,
            values=["Random Forest", "SVM", "XGBoost"],
            state="readonly"
        )
        self.model_combobox.pack(fill=tk.X, pady=5)
        self.model_combobox.current(0)

        # Tahmin butonu
        self.predict_btn = ttk.Button(
            right_frame,
            text="Tahmin Yap",
            command=self.predict_failure,
            state=tk.DISABLED
        )
        self.predict_btn.pack(pady=10)
        self.result_label = ttk.Label(right_frame, text="", wraplength=180)
        self.result_label.pack()

    def create_bottom_panel(self):
        """Alt panel: Risk listesi ve raporlama butonları."""
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=5, pady=5)

        # Başlık
        self.risk_title_label = ttk.Label(
            bottom_frame,
            text="Yüksek Riskli Makineler (Top 1-20)",
            font=('Helvetica', 12, 'bold')
        )
        self.risk_title_label.pack()

        # Treeview (Tablo görünümü)
        self.risk_tree = ttk.Treeview(
            bottom_frame,
            columns=("machine_id", "risk_score"),
            show="headings",
            height=8
        )
        self.risk_tree.heading("machine_id", text="Makine ID")
        self.risk_tree.heading("risk_score", text="Risk Skoru")
        self.risk_tree.column("machine_id", width=150)
        self.risk_tree.column("risk_score", width=100)
        self.risk_tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(bottom_frame, orient="vertical", command=self.risk_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.risk_tree.configure(yscrollcommand=scrollbar.set)

        # Sayfalama ve rapor butonları
        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.next_page_btn = ttk.Button(
            button_frame,
            text="Sonraki 20 Makineyi Göster",
            command=self.show_next_risk_page
        )
        self.next_page_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Rapor Oluştur (CSV)",
            command=self.export_risk_report
        ).pack(side=tk.LEFT, padx=5)

        self.risk_tree.bind("<Double-1>", self.on_risk_tree_select)

    # ---------------------- İŞLEVSEL METODLAR ----------------------

    def filter_machines(self, event):
        """Arama kutusuna girilen metne göre makine listesini filtreler."""
        search_term = self.search_entry.get().lower()
        self.machine_listbox.delete(0, tk.END)
        for machine_id in sorted(self.manager.machines.keys()):
            if search_term in machine_id.lower():
                self.machine_listbox.insert(tk.END, machine_id)

    def refresh_machine_list(self):
        """Makine listesini veritabanından yeniden yükler."""
        self.machine_listbox.delete(0, tk.END)
        for machine_id in sorted(self.manager.machines.keys()):
            self.machine_listbox.insert(tk.END, machine_id)

    def on_machine_select(self, event):
        """Listeden makine seçildiğinde detayları gösterir."""
        selected = self.machine_listbox.curselection()
        if selected:
            self.selected_machine_id = self.machine_listbox.get(selected[0])
            self.show_machine_details()
            self.predict_btn.config(state=tk.NORMAL)

    def show_machine_details(self):
        """Seçili makinenin detaylarını text alanında gösterir."""
        machine = self.manager.machines[self.selected_machine_id]
        self.detail_text.config(state=tk.NORMAL)
        self.detail_text.delete(1.0, tk.END)

        details = (
            f"Makine ID: {machine.machine_id}\n"
            f"Tip: {machine.machine_type}\n"
            f"Hava Sıcaklığı: {machine.features['air_temp']} K\n"
            f"İşlem Sıcaklığı: {machine.features['process_temp']} K\n"
            f"Dönüş Hızı: {machine.features['rotational_speed']} rpm\n"
            f"Tork: {machine.features['torque']} Nm\n"
            f"Takım Aşınması: {machine.features['tool_wear']} min\n"
            f"Arıza Durumu: {'VAR' if machine.features['failure'] else 'YOK'}"
        )

        self.detail_text.insert(tk.END, details)
        self.detail_text.config(state=tk.DISABLED)

    def load_model(self):
        """Seçili modeli diskten yükler."""
        model_name = self.model_var.get().lower().replace(" ", "_")
        try:
            self.loaded_model = joblib.load(f"models/trained_models/classification/{model_name}.joblib")
            return True
        except Exception as e:
            messagebox.showerror("Hata", f"Model yüklenemedi:\n{str(e)}")
            return False

    def predict_failure(self):
        """Seçili makine için arıza tahmini yapar."""
        if not self.load_model():
            return

        try:
            machine = self.manager.machines[self.selected_machine_id]
            features = pd.DataFrame([[
                machine.features['air_temp'],
                machine.features['process_temp'],
                machine.features['rotational_speed'],
                machine.features['torque'],
                machine.features['tool_wear']
            ]], columns=['air_temp', 'process_temp', 'rotational_speed', 'torque', 'tool_wear'])

            proba = self.loaded_model.predict_proba(features)[0][1]
            result_text = (
                f"Arıza Olasılığı: {proba * 100:.2f}%\n"
                f"Risk Seviyesi: {'🔴 YÜKSEK' if proba > 0.7 else '🟡 ORTA' if proba > 0.3 else '🟢 DÜŞÜK'}"
            )
            self.result_label.config(text=result_text)

        except Exception as e:
            messagebox.showerror("Hata", f"Tahmin başarısız:\n{str(e)}")

    def get_all_machines_features(self):
        """Tüm makinelerin özelliklerini DataFrame olarak döndürür."""
        features = []
        for machine_id, machine in self.manager.machines.items():
            features.append({
                'machine_id': machine_id,
                'type': machine.machine_type,
                **machine.features
            })
        return pd.DataFrame(features)

    def refresh_high_risk_list(self):
        """Risk listesini günceller."""
        if not self.load_model():
            return

        try:
            df = self.get_all_machines_features()
            X = df[['air_temp', 'process_temp', 'rotational_speed', 'torque', 'tool_wear']]
            df['risk_score'] = self.loaded_model.predict_proba(X)[:, 1]

            start_idx = self.current_risk_page * 20
            top_risky = df.nlargest(40, 'risk_score').iloc[start_idx:start_idx + 20]

            self.risk_tree.delete(*self.risk_tree.get_children())
            for _, row in top_risky.iterrows():
                risk_level = "high" if row['risk_score'] > 0.7 else "medium" if row['risk_score'] > 0.3 else "low"
                self.risk_tree.insert(
                    "", "end",
                    values=(row['machine_id'], f"{row['risk_score'] * 100:.1f}%"),
                    tags=(risk_level,)
                )

            # Başlık ve buton güncelleme
            page_range = "21-40" if self.current_risk_page == 1 else "1-20"
            self.risk_title_label.config(text=f"Yüksek Riskli Makineler (Top {page_range})")
            self.next_page_btn.config(
                text="İlk 20 Makineyi Göster" if self.current_risk_page == 1 else "Sonraki 20 Makineyi Göster"
            )

            # Renk etiketleri
            self.risk_tree.tag_configure('high', background='#ffdddd')
            self.risk_tree.tag_configure('medium', background='#fff3cd')
            self.risk_tree.tag_configure('low', background='#e6ffe6')

        except Exception as e:
            messagebox.showerror("Hata", f"Risk listesi oluşturulamadı:\n{str(e)}")

    def show_next_risk_page(self):
        """Risk listesi sayfaları arasında geçiş yapar."""
        self.current_risk_page = 1 if self.current_risk_page == 0 else 0
        self.refresh_high_risk_list()

    def on_risk_tree_select(self, event):
        """Risk listesinden çift tıklanan makineyi seçer."""
        item = self.risk_tree.selection()[0]
        machine_id = self.risk_tree.item(item, "values")[0]
        self.selected_machine_id = machine_id
        items = self.machine_listbox.get(0, tk.END)
        if machine_id in items:
            idx = items.index(machine_id)
            self.machine_listbox.selection_clear(0, tk.END)
            self.machine_listbox.selection_set(idx)
            self.machine_listbox.see(idx)
        self.show_machine_details()
        self.predict_btn.config(state=tk.NORMAL)

    def update_machine_features(self):
        """Makine özelliklerini güncellemek için pencere açar."""
        if not self.selected_machine_id:
            return

        machine = self.manager.machines[self.selected_machine_id]
        top = tk.Toplevel(self.root)
        top.title("Makine Özelliklerini Güncelle")
        top.grab_set()

        features = [
            ('air_temp', 'Hava Sıcaklığı (K)'),
            ('process_temp', 'İşlem Sıcaklığı (K)'),
            ('rotational_speed', 'Dönüş Hızı (rpm)'),
            ('torque', 'Tork (Nm)'),
            ('tool_wear', 'Takım Aşınması (min)')
        ]

        entries = {}
        for i, (feature, label) in enumerate(features):
            ttk.Label(top, text=label).grid(row=i, column=0, padx=5, pady=5, sticky=tk.E)
            entries[feature] = ttk.Entry(top)
            entries[feature].grid(row=i, column=1, padx=5, pady=5)
            entries[feature].insert(0, str(machine.features[feature]))

        def save_changes():
            for feature in entries:
                try:
                    machine.features[feature] = float(entries[feature].get())
                except ValueError:
                    messagebox.showerror("Hata", f"Geçersiz değer: {feature}")
                    return

            machine.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            machine.save_to_file()
            self.show_machine_details()
            self.refresh_high_risk_list()  # Risk listesini yenile
            top.destroy()

        ttk.Button(top, text="Kaydet", command=save_changes).grid(
            row=len(features), column=0, columnspan=2, pady=10)

    def export_risk_report(self):
        """Risk listesini CSV olarak dışa aktarır."""
        if not self.loaded_model:
            messagebox.showwarning("Uyarı", "Önce bir model yükleyin!")
            return

        try:
            df = self.get_all_machines_features()
            X = df[['air_temp', 'process_temp', 'rotational_speed', 'torque', 'tool_wear']]
            df['risk_score'] = self.loaded_model.predict_proba(X)[:, 1]

            start_idx = self.current_risk_page * 20
            top_risky = df.nlargest(40, 'risk_score').iloc[start_idx:start_idx + 20]

            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Dosyası", "*.csv"), ("Tüm Dosyalar", "*.*")],
                title="Raporu Kaydet"
            )

            if file_path:
                top_risky.to_csv(file_path, index=False, float_format="%.2f", encoding='utf-8-sig')
                messagebox.showinfo("Başarılı", f"Rapor kaydedildi:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Hata", f"Rapor oluşturulamadı:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = PredictiveMaintenanceApp(root)
    root.mainloop()