import time
import requests

BACKEND_URL = "https://meeting-bot-backend.onrender.com"


def main():
    print("🚀 Worker Render démarré (bot cloud).")

    while True:
        try:
            # Récupérer la prochaine réunion à rejoindre
            resp = requests.get(f"{BACKEND_URL}/next_meeting_to_join", timeout=10)
            resp.raise_for_status()
            meeting = resp.json()
        except Exception as e:
            print("❌ Erreur en contactant le backend :", e)
            time.sleep(30)
            continue

        status = meeting.get("status")

        if status == "none":
            print("Aucune réunion à rejoindre pour le moment.")
        else:
            mid = meeting.get("id")
            title = meeting.get("title")
            url = meeting.get("meeting_url")
            start_time = meeting.get("start_time")

            print("🔔 Réunion trouvée à rejoindre :")
            print(f"- ID       : {mid}")
            print(f"- Titre    : {title}")
            print(f"- URL      : {url}")
            print(f"- Début    : {start_time}")

            # 🔑 NOUVEAU : marquer la réunion comme "in_progress"
            try:
                mark_resp = requests.post(
                    f"{BACKEND_URL}/mark_meeting_started",
                    json={"meeting_id": mid},
                    timeout=10,
                )
                mark_resp.raise_for_status()
                print("✅ Réunion marquée comme 'in_progress' côté backend.")
            except Exception as e:
                print("❌ Erreur lors du marquage 'in_progress' :", e)

            print("👉 (Étape suivante : ici le bot rejoindra la réunion en headless)")

        # on attend 30 secondes avant de re-check
        time.sleep(30)


if __name__ == "__main__":
    main()
