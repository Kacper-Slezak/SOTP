import asyncio
from datetime import datetime, timedelta, timezone

from backend.app.models.device import Device
from backend.app.models.metric import DeviceMetric
from backend.app.models.user import User, UserRole
from backend.app.utils.databases import create_postgres, create_timescaledb
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import async_sessionmaker

# Generate a proper password hash for "admin123"
# You can change this password by running:
# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# print(pwd_context.hash("your_password_here"))
DEFAULT_PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5OwGJ7C9qVYWS"  # Hash for "admin123"


async def seed_data():
    """Initializes and seeds the PostgreSQL and TimescaleDB databases."""

    print("Initializing database engines...")
    postgres_engine = create_postgres()
    timescale_engine = create_timescaledb()

    SessionPG = async_sessionmaker(postgres_engine, expire_on_commit=False)
    SessionTS = async_sessionmaker(timescale_engine, expire_on_commit=False)

    async with SessionPG() as session_pg:
        print("Connected to PostgreSQL.")

        # --- 1. Create Default User (Admin) ---
        # Check if user exists first
        result = await session_pg.execute(
            select(User).where(User.email == "admin@sotp.local")
        )
        default_user = result.scalar_one_or_none()

        if default_user:
            print(f"User admin@sotp.local already exists (ID: {default_user.id})")
        else:
            default_user = User(
                email="admin@sotp.local",
                name="System Administrator",
                password_hash=DEFAULT_PASSWORD_HASH,
                role=UserRole.ADMIN,
                is_active=True,
            )
            session_pg.add(default_user)
            await session_pg.commit()
            await session_pg.refresh(default_user)
            print(f"Created user: {default_user.email} (ID: {default_user.id})")

        # --- 2. Create Demo Devices ---
        if default_user:
            demo_devices = [
                Device(
                    name="Core-Router-01",
                    ip_address="192.168.1.1",
                    device_type="router",
                    vendor="Cisco",
                    model="ISR 4331",
                    os_version="IOS-XE 17.6",
                    location="Server Room A",
                    is_active=True,
                    created_by_id=default_user.id,
                    snmp_config='{"community": "public"}',
                    ssh_config='{"username": "admin"}',
                ),
                Device(
                    name="Edge-Switch-05",
                    ip_address="10.0.0.5",
                    device_type="switch",
                    vendor="Juniper",
                    model="EX4300",
                    os_version="Junos 20.4",
                    location="Floor 3, IDF",
                    is_active=True,
                    created_by_id=default_user.id,
                ),
                Device(
                    name="Linux-Server-Web",
                    ip_address="172.16.0.10",
                    device_type="server",
                    vendor="Dell",
                    model="PowerEdge R650",
                    os_version="Ubuntu 22.04",
                    location="Data Center",
                    is_active=False,  # Example of an inactive device
                    created_by_id=default_user.id,
                ),
            ]

            device_map = {}
            for device in demo_devices:
                # Check if device exists (by name or IP)
                result = await session_pg.execute(
                    select(Device).where(
                        (Device.name == device.name)
                        | (Device.ip_address == device.ip_address)
                    )
                )
                existing_device = result.scalar_one_or_none()

                if existing_device:
                    device_map[device.name] = existing_device.id
                    print(
                        f"Device {device.name} already exists (ID: {existing_device.id})"
                    )
                else:
                    session_pg.add(device)
                    await session_pg.commit()
                    await session_pg.refresh(device)
                    device_map[device.name] = device.id
                    print(f"Added device: {device.name} (ID: {device.id})")

            # Get the router ID for metrics insertion
            router_id = device_map.get("Core-Router-01")

            if not router_id:
                print(" WARNING: Core-Router-01 not found. Skipping metrics insertion.")
                return

    # --- 3. Insert Demo Metrics into TimescaleDB ---
    async with SessionTS() as session_ts:
        print("Connected to TimescaleDB.")

        # Check if metrics already exist for this device
        result = await session_ts.execute(
            select(DeviceMetric).where(DeviceMetric.device_id == router_id).limit(1)
        )
        existing_metrics = result.scalar_one_or_none()

        if existing_metrics:
            print(
                f"Metrics for Core-Router-01 already exist. Skipping metrics insertion."
            )
        else:
            metric_data = []
            now = datetime.now(timezone.utc)

            # Generate 2 hours of fake CPU utilization data (every 5 minutes)
            for i in range(24):  # 24 x 5 mins = 120 mins (2 hours)
                time_point = now - timedelta(minutes=i * 5)

                # Create a fake CPU load value (e.g., 50% to 75%)
                cpu_value = 50 + (i % 5) * 5 + (i % 2)

                metric_data.append(
                    {
                        "time": time_point,
                        "device_id": router_id,
                        "metric_name": "cpu_utilization",
                        "value": cpu_value,
                    }
                )

                # Create a fake memory usage value (e.g., 30% to 40%)
                memory_value = 30 + (i % 3) * 3

                metric_data.append(
                    {
                        "time": time_point,
                        "device_id": router_id,
                        "metric_name": "memory_usage",
                        "value": memory_value,
                    }
                )

            if metric_data:
                await session_ts.execute(insert(DeviceMetric), metric_data)
                await session_ts.commit()
                print(
                    f"Inserted {len(metric_data)} historical metrics for Core-Router-01."
                )

        print("\n Seeding complete!")
        print(f"\n Default credentials:")
        print(f"   Email: admin@sotp.local")
        print(f"   Password: admin123")


async def main():
    """Wrapper function to run the async seeding function."""
    # Ensure .env variables are loaded
    from dotenv import load_dotenv

    load_dotenv(override=True)

    await seed_data()


if __name__ == "__main__":
    # Ensure that running directly works as expected
    try:
        asyncio.run(main())
    except ImportError:
        print("\ ERROR: This script requires the backend dependencies to be installed.")
        print(
            "   Try running 'pip install -r backend/requirements.txt' in your environment or use 'make test' for container execution."
        )
    except Exception as e:
        print(f"\ A critical error occurred during seeding: {e}")
        print(
            "   Ensure your Docker containers (postgres, timescale) are running and healthy. You can run: 'make dev'"
        )
        import traceback

        traceback.print_exc()
