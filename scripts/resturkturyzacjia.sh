#!/bin/bash

# 1. Tworzenie głównego folderu na aplikacje
echo "📂 Tworzenie struktury katalogów apps/..."
mkdir -p apps

# 2. Przenoszenie Backendu (Core) i Frontendu
echo "🚚 Przenoszenie Core Backend i Frontend..."
mv backend apps/core-backend
mv frontend apps/web-frontend

# 3. Tworzenie struktury Network Workera (kopia z backendu jako baza)
echo "🔧 Tworzenie Network Workera..."
mkdir -p apps/network-worker/src/app
# Kopiujemy Dockerfile i requirements jako punkt startowy
cp apps/core-backend/Dockerfile apps/network-worker/
cp apps/core-backend/requirements.txt apps/network-worker/
# Tworzymy puste pliki, żeby struktura istniała
touch apps/network-worker/src/main.py

# 4. EKSTRAKCJA LOGIKI SIECIOWEJ (To jest kluczowy moment!)
# Przenosimy zadania monitoringu z Core do Workera
if [ -f "apps/core-backend/app/tasks/monitoring_tasks.py" ]; then
    echo "📦 Przenoszenie zadań monitoringu do Workera..."
    mv apps/core-backend/app/tasks/monitoring_tasks.py apps/network-worker/src/app/worker.py
fi

# Jeśli masz folder collectors, przenosimy go też (zakładam, że mógł powstać)
if [ -d "apps/core-backend/app/collectors" ]; then
    echo "📦 Przenoszenie kolektorów (SNMP/ICMP) do Workera..."
    mv apps/core-backend/app/collectors apps/network-worker/src/app/
fi

# 5. Tworzenie SOTP Agenta (Puste miejsce pod nowy serwis)
echo "🕵️ Tworzenie struktury Agenta..."
mkdir -p apps/sotp-agent
touch apps/sotp-agent/agent.py
touch apps/sotp-agent/requirements.txt
touch apps/sotp-agent/Dockerfile

# 6. Aktualizacja Infrastruktury (Docker Compose)
echo "🛠 Aktualizacja ścieżek w Docker Compose..."
# Używamy sed do zmiany ścieżek ./backend na ./apps/core-backend itd.
# Ta komenda działa na Linuxie (na macOS dodaj '' po -i)
sed -i 's|./backend|./apps/core-backend|g' infrastructure/docker/docker-compose.dev.yml
sed -i 's|./frontend|./apps/web-frontend|g' infrastructure/docker/docker-compose.dev.yml

# 7. Tworzenie miejsca na Kubernetes (Helm)
echo "kubernetes" > infrastructure/.k8s_placeholder
mkdir -p infrastructure/k8s/charts

echo "✅ ZAKOŃCZONO! Twoje repozytorium jest teraz w architekturze Multi-Service."
echo "⚠️  PAMIĘTAJ: Musisz teraz ręcznie poprawić importy w plikach Python (np. w worker.py)."
