import subprocess
from datetime import datetime

# ====== CONFIG ======
curl_commands = [
    # --- Status & Général ---
    'curl -X GET "http://127.0.0.1:40631/v1/status"',
    'curl -X GET "http://127.0.0.1:40631/mode"',
    'curl -X GET "http://127.0.0.1:40631/onboarding"',
    'curl -X GET "http://127.0.0.1:40631/features"',
    'curl -X GET "http://127.0.0.1:40631/content/inAppToastMessage"',
    'curl -X GET "http://127.0.0.1:40631/keyboardShortcuts"',

    # --- Gestion des Volumes (Mixer) ---
    'curl -X GET "http://127.0.0.1:40631/volumeSettings/classic"',
    'curl -X GET "http://127.0.0.1:40631/volumeSettings/streamer"',
    'curl -X GET "http://127.0.0.1:40631/volumeSettings/devices/volumes"',
    'curl -X GET "http://127.0.0.1:40631/chatMix"',

    # --- Périphériques Audio & Routage ---
    'curl -X GET "http://127.0.0.1:40631/audioDevices"',
    'curl -X GET "http://127.0.0.1:40631/deviceOut"',
    'curl -X GET "http://127.0.0.1:40631/AudioDeviceRouting"',
    'curl -X GET "http://127.0.0.1:40631/classicRedirections"',
    'curl -X GET "http://127.0.0.1:40631/streamRedirections"',
    'curl -X GET "http://127.0.0.1:40631/streamRedirections/isStreamMonitoringEnabled"',
    'curl -X GET "http://127.0.0.1:40631/streamRedirections/isStreamMonitoringLocked"',
    'curl -X GET "http://127.0.0.1:40631/linkAll/isRenderLinkAllEnabled"',

    # --- Configurations & Profils (EQ) ---
    'curl -X GET "http://127.0.0.1:40631/configs"',
    'curl -X GET "http://127.0.0.1:40631/configs/selected"',
    'curl -X GET "http://127.0.0.1:40631/configs/options"',
    # Récupération des configs par défaut pour chaque canal virtuel
    'curl -X GET "http://127.0.0.1:40631/configs/default?virtualAudioDevice=game"',
    'curl -X GET "http://127.0.0.1:40631/configs/default?virtualAudioDevice=chatRender"',
    'curl -X GET "http://127.0.0.1:40631/configs/default?virtualAudioDevice=media"',
    'curl -X GET "http://127.0.0.1:40631/configs/default?virtualAudioDevice=aux"',
    'curl -X GET "http://127.0.0.1:40631/configs/default?virtualAudioDevice=chatCapture"',

    # --- Paramètres de Fallback (Backup audio) ---
    'curl -X GET "http://127.0.0.1:40631/fallbackSettings/isEnabled"',
    'curl -X GET "http://127.0.0.1:40631/fallbackSettings/isWirelessTriggerEnabled"',
    'curl -X GET "http://127.0.0.1:40631/fallbackSettings/isFallbackOnRebootEnabled"',
    'curl -X GET "http://127.0.0.1:40631/fallbackSettings/lists"',

    # --- Quickset (Paramètres rapides) ---
    'curl -X GET "http://127.0.0.1:40631/quickset/isEnabled"',
    'curl -X GET "http://127.0.0.1:40631/quickset/selected"',
    'curl -X GET "http://127.0.0.1:40631/quickset/profiles"',

    # --- Fonctionnalités Hardware spécifiques ---
    'curl -X GET "http://127.0.0.1:40631/features/Bindable"',
    'curl -X GET "http://127.0.0.1:40631/features/LineOut"',
    'curl -X GET "http://127.0.0.1:40631/features/HeadphoneOut"',
    'curl -X GET "http://127.0.0.1:40631/features/BuiltInEq"',

    # --- Overlays & Enregistrement ---
    'curl -X GET "http://127.0.0.1:40631/overlays"',
    'curl -X GET "http://127.0.0.1:40631/overlays/isHardwareTriggeredEnabled"',
    'curl -X GET "http://127.0.0.1:40631/audioSamples/isRecording"',
]

output_file = "resultats_curl.txt"
# ====================


def run_curl_commands(commands, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"=== Début exécution : {datetime.now()} ===\n\n")

        for i, cmd in enumerate(commands, start=1):
            f.write(f"\n{'='*60}\n")
            f.write(f"Commande #{i}:\n{cmd}\n")
            f.write(f"{'-'*60}\n")

            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True
                )

                f.write("Sortie STDOUT:\n")
                f.write(result.stdout + "\n")

                # if result.stderr:
                #     f.write("\nSortie STDERR:\n")
                #     f.write(result.stderr + "\n")

                # f.write(f"\nCode de retour: {result.returncode}\n")

            except Exception as e:
                f.write(f"\nErreur d'exécution: {str(e)}\n")

        f.write(f"\n=== Fin exécution : {datetime.now()} ===\n")


if __name__ == "__main__":
    run_curl_commands(curl_commands, output_file)
    print(f"✔ Toutes les requêtes ont été exécutées.")
    print(f"📄 Résultats enregistrés dans : {output_file}")