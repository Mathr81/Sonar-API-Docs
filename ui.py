import os
import json
import requests
import threading
import customtkinter as ctk
from tkinter import messagebox

# Configuration de l'apparence
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class SonarController(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sonar Mini-Controller")
        self.geometry("400x600") # Un peu plus grand pour être sûr
        self.resizable(False, False)

        self.base_url = None
        self.devices_map = {} 
        self.channels = [
            ("Master", "Master"),
            ("Jeu (Game)", "game"),
            ("Chat (Discord)", "chatRender"),
            ("Média", "media"),
            ("Aux", "aux"),
            ("Microphone", "chatCapture")
        ]
        
        # Interface de chargement
        self.loading_label = ctk.CTkLabel(self, text="Recherche de Sonar...", font=("Arial", 16))
        self.loading_label.pack(pady=200)

        # Lancer la connexion en arrière-plan
        threading.Thread(target=self.connect_to_sonar, daemon=True).start()

    def connect_to_sonar(self):
        """Trouve le port et l'adresse de Sonar"""
        try:
            path = r"C:\ProgramData\SteelSeries\GG\coreProps.json"
            if not os.path.exists(path):
                raise Exception("SteelSeries GG n'est pas installé ou le fichier est introuvable.")

            with open(path, "r") as f:
                data = json.load(f)
            
            gg_address = data.get("ggEncryptedAddress")
            if not gg_address:
                raise Exception("Impossible de trouver l'adresse GG.")

            try:
                # verify=False est CRUCIAL ici
                r = requests.get(f"https://{gg_address}/subApps", verify=False, timeout=5)
            except requests.exceptions.ConnectionError:
                 raise Exception("Impossible de se connecter à GG (vérifie qu'il est lancé).")

            if r.status_code != 200:
                raise Exception(f"Erreur de connexion à GG: {r.status_code}")
            
            # --- CORRECTION DU PARSING ICI ---
            json_response = r.json()
            
            # On cherche la clé 'subApps' dans la réponse, sinon on prend la racine (compatibilité)
            apps_list = json_response.get("subApps", json_response)
            
            if "sonar" not in apps_list:
                raise Exception("Sonar n'est pas actif.\nOuvrez l'onglet 'Sonar' dans GG une fois pour le lancer.")

            sonar_metadata = apps_list["sonar"].get("metadata", {})
            web_server_address = sonar_metadata.get("webServerAddress")
            encrypted_address = sonar_metadata.get("encryptedWebServerAddress")

            # Gestion du cas où l'adresse HTTP est vide (nouveau comportement GG)
            if web_server_address and web_server_address != "":
                self.base_url = f"http://{web_server_address}" if not web_server_address.startswith("http") else web_server_address
            elif encrypted_address:
                # Fallback sur HTTPS
                self.base_url = f"https://{encrypted_address}" if not encrypted_address.startswith("http") else encrypted_address
            else:
                raise Exception("L'adresse de Sonar est introuvable.")

            # Une fois connecté, on force le mode Classic et on construit l'UI
            self.ensure_classic_mode()
            self.after(0, self.build_interface)

        except Exception as e:
            err_message = str(e)
            print(f"DEBUG ERREUR: {err_message}")
            self.after(0, lambda: messagebox.showerror("Erreur Critique", err_message))

    def ensure_classic_mode(self):
        """Force le mode Classic comme demandé"""
        try:
            requests.put(f"{self.base_url}/mode/classic", timeout=2)
        except:
            pass

    def build_interface(self):
        """Construit l'interface graphique une fois connecté"""
        self.loading_label.destroy()

        # --- Section Périphérique ---
        device_frame = ctk.CTkFrame(self)
        device_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(device_frame, text="Sortie Audio (Output)", font=("Arial", 14, "bold")).pack(pady=5)
        
        self.device_var = ctk.StringVar(value="Chargement...")
        self.device_menu = ctk.CTkOptionMenu(device_frame, variable=self.device_var, command=self.change_device)
        self.device_menu.pack(pady=5, padx=10, fill="x")

        # --- Section Mixeur ---
        mixer_frame = ctk.CTkScrollableFrame(self, label_text="Mixer (Classic Mode)")
        mixer_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.sliders = {}
        self.mutes = {}

        for label_text, channel_code in self.channels:
            # Container pour chaque canal
            row = ctk.CTkFrame(mixer_frame, fg_color="transparent")
            row.pack(fill="x", pady=5)

            # Label
            ctk.CTkLabel(row, text=label_text, width=100, anchor="w").pack(side="left", padx=5)

            # Slider
            # On passe une commande qui appelle set_volume
            slider = ctk.CTkSlider(row, from_=0, to=1, command=lambda v, c=channel_code: self.set_volume(c, v))
            slider.pack(side="left", fill="x", expand=True, padx=5)
            self.sliders[channel_code] = slider

            # Mute Switch
            mute_var = ctk.BooleanVar()
            mute_switch = ctk.CTkCheckBox(row, text="Mute", variable=mute_var, width=60, 
                                          command=lambda c=channel_code: self.toggle_mute(c))
            mute_switch.pack(side="right", padx=5)
            self.mutes[channel_code] = mute_var

        # Bouton refresh manuel au cas où
        ctk.CTkButton(self, text="Rafraîchir", command=self.refresh_data).pack(pady=10)

        # Charger les données initiales
        self.refresh_data()

    def refresh_data(self):
        """Récupère les volumes actuels et la liste des devices"""
        threading.Thread(target=self._refresh_data_thread, daemon=True).start()

    def _refresh_data_thread(self):
        try:
            # 1. Récupérer les devices
            try:
                r_dev = requests.get(f"{self.base_url}/audioDevices", timeout=2)
                if r_dev.status_code == 200:
                    devices = r_dev.json()
                    # On ne garde que les sorties (render)
                    self.devices_map = {d['friendlyName']: d['id'] for d in devices if d['dataFlow'] == 'render'}
                    
                    device_names = list(self.devices_map.keys())
                    
                    # Mise à jour UI sur le thread principal
                    def update_devices():
                        self.device_menu.configure(values=device_names)
                        if device_names and self.device_var.get() == "Chargement...":
                            self.device_var.set(device_names[0])
                    self.after(0, update_devices)
            except Exception as e:
                print(f"Erreur Devices: {e}")

            # 2. Récupérer les volumes
            try:
                r_vol = requests.get(f"{self.base_url}/volumeSettings/classic", timeout=2)
                if r_vol.status_code == 200:
                    data = r_vol.json()
                    
                    def get_vol_data(channel):
                        if channel == "Master":
                            return data.get("masters", {}).get("classic", {})
                        return data.get("devices", {}).get(channel, {}).get("classic", {})

                    # Préparation des mises à jour UI
                    updates = []
                    for _, channel in self.channels:
                        vol_data = get_vol_data(channel)
                        if vol_data:
                            vol = vol_data.get("volume", 0.5)
                            muted = vol_data.get("muted", False)
                            updates.append((channel, vol, muted))
                    
                    # Appliquer les mises à jour sur le thread principal
                    def apply_updates():
                        for ch, vol, is_muted in updates:
                            if ch in self.sliders:
                                self.sliders[ch].set(vol)
                            if ch in self.mutes:
                                self.mutes[ch].set(is_muted)
                    
                    self.after(0, apply_updates)

            except Exception as e:
                print(f"Erreur Volumes: {e}")

        except Exception as e:
            print(f"Erreur globale refresh: {e}")

    def set_volume(self, channel, value):
        """Appelle l'API pour changer le volume (Threadé pour éviter le lag UI)"""
        def send():
            try:
                requests.put(f"{self.base_url}/volumeSettings/classic/{channel}/Volume/{value}", timeout=1)
            except Exception as e:
                print(f"Erreur set volume {channel}: {e}")
        threading.Thread(target=send, daemon=True).start()

    def toggle_mute(self, channel):
        """Appelle l'API pour changer le mute"""
        def send():
            try:
                # On récupère la valeur actuelle de la variable associée
                is_checked = self.mutes[channel].get()
                state = "true" if is_checked else "false"
                requests.put(f"{self.base_url}/volumeSettings/classic/{channel}/Mute/{state}", timeout=1)
            except Exception as e:
                print(f"Erreur set mute {channel}: {e}")
        threading.Thread(target=send, daemon=True).start()

    def change_device(self, device_name):
        """Change le périphérique de sortie"""
        def send():
            try:
                device_id = self.devices_map.get(device_name)
                if device_id:
                    url = f"{self.base_url}/classicRedirections/render/deviceId/{device_id}"
                    requests.put(url, timeout=2)
                    print(f"Device changé pour: {device_name}")
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Erreur Device", str(e)))
        
        threading.Thread(target=send, daemon=True).start()

if __name__ == "__main__":
    # Désactiver les avertissements SSL pour localhost
    requests.packages.urllib3.disable_warnings()
    
    app = SonarController()
    app.mainloop()