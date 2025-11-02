from typing import Sequence

from sqlalchemy.future import select

# 2. Zaimportuj swój model Device (zakładam, że masz go np. tutaj)
from app.db.postgres_session import get_postgres_session
from app.models.device import Device

# 1. Importuj context manager dla sesji Postgres


async def get_all_devices() -> Sequence[Device]:

    # 3. Użyj context managera, aby automatycznie zarządzać sesją
    async with get_postgres_session() as db:

        # 'db' to teraz aktywna sesja AsyncSession

        # 4. Zbuduj zapytanie SELECT * FROM devices
        query = select(Device).order_by(Device.id)  # Sortowanie jest opcjonalne

        # 5. Wykonaj zapytanie asynchronicznie
        result = await db.execute(query)

        # 6. Pobierz obiekty i zwróć listę
        # .scalars() pobiera same obiekty 'Device'
        # .all() tworzy z nich listę
        devices = result.scalars().all()

        return devices
