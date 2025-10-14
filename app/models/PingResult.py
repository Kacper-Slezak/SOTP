from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Float,
    Boolean as Bool,
    String,
    func,
)
from sqlalchemy.orm import relationship

# Zakładam, że Base jest dostępna poprzez import, tak jak w pliku device.py
from .base import Base


class PingResult(Base):
    __tablename__ = "ping_results"

    id = Column(Integer, primary_key=True, index=True)
    
    # Klucz obcy do tabeli 'devices'
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    
    # --- Metryki Pingu ---
    
    # Status ogólny pingu (np. True = UP, False = DOWN)
    is_alive = Column(Bool, nullable=False, index=True) 
    
    # Średni czas odpowiedzi w milisekundach (RTT), może być NULL jeśli pingu nie było
    rtt_avg_ms = Column(Float, nullable=True) 
    
    # Opcjonalne: Użyteczne dla pełniejszej diagnostyki (np. icmplib zwraca te dane)
    packet_loss_percent = Column(Float, nullable=True) 
    
    # Czas pomiaru - kluczowy dla serii czasowych (np. w TimescaleDB)
    timestamp = Column(DateTime, default=func.now(), index=True, nullable=False)
    
    # Dodatkowe informacje diagnostyczne (opcjonalne)
    diagnostic_message = Column(String, nullable=True) 

    # --- Relacja (opcjonalnie, ale zalecane dla spójności) ---
    
    # Relacja do urządzenia, które zostało spingowane.
    # Musisz dodać 'ping_results = relationship("PingResult", ...)' 
    # do klasy Device w pliku device.py
    device = relationship("Device", backref="ping_results") 

    def __repr__(self):
        status = "UP" if self.is_alive else "DOWN"
        rtt = f"{self.rtt_avg_ms:.2f}ms" if self.rtt_avg_ms is not None else "N/A"
        return f"<PingResult(device_id={self.device_id}, status='{status}', rtt={rtt})>"