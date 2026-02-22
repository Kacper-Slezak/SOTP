import asyncio
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.tasks.snmp_collector import (
    OIDS,
    collect_device_snmp,
    get_active_devices,
    save_metrics,
    schedule_all_snmp,
    snmp_get_all,
)

# ==========================================
# 1. PROSTE TESTY JEDNOSTKOWE (LOGIKA SNMP)
# ==========================================


class TestSNMPLogic:

    @patch("app.tasks.snmp_collector.snmp")
    @patch("app.tasks.snmp_collector.Config")
    def test_snmp_get_all_success(self, mock_config, mock_snmp):
        mock_config.SNMP_USER = "test_user"
        mock_config.SNMP_AUTH = "test_auth"
        mock_config.SNMP_PRIV = "test_priv"

        mock_var_binds = [
            (MagicMock(), MagicMock(__str__=lambda x: "123456")),
            (MagicMock(), MagicMock(__str__=lambda x: "20")),
            (MagicMock(), MagicMock(__str__=lambda x: "8192")),
            (MagicMock(), MagicMock(__str__=lambda x: "4096")),
            (MagicMock(), MagicMock(__str__=lambda x: "5")),
        ]

        async def fake_get_cmd(*args, **kwargs):
            return (None, None, 0, mock_var_binds)

        mock_snmp.get_cmd = fake_get_cmd

        async def fake_create(*args, **kwargs):
            return MagicMock()

        mock_snmp.UdpTransportTarget.create = fake_create

        result = snmp_get_all("127.0.0.1")

        assert len(result) == 5
        assert result["uptime"] == "123456"
        assert result["cpu_load"] == "20"


# ==========================================
# 2. TESTY INTEGRACYJNE (BEZ INICJALIZACJI MODELI)
# ==========================================


class TestSNMPDatabaseAndCelery:

    @pytest.mark.asyncio
    @patch("app.tasks.snmp_collector.get_postgres_session")
    async def test_get_active_devices(self, mock_get_pg_session):
        fake_device_1 = MagicMock()
        fake_device_1.id = 1
        fake_device_1.ip_address = "192.168.1.10"
        fake_device_1.is_active = True

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [fake_device_1]
        mock_session.execute.return_value = mock_result

        @asynccontextmanager
        async def mock_session_manager():
            yield mock_session

        mock_get_pg_session.return_value = mock_session_manager()
        devices = await get_active_devices()

        assert len(devices) == 1
        assert devices[0].ip_address == "192.168.1.10"

    @pytest.mark.asyncio
    @patch("app.tasks.snmp_collector.DeviceMetric")
    @patch("app.tasks.snmp_collector.get_timescale_session")
    async def test_save_metrics(self, mock_get_ts_session, mock_metric_class):
        mock_session = MagicMock()
        mock_session.execute = AsyncMock()

        @asynccontextmanager
        async def mock_session_manager():
            yield mock_session

        mock_get_ts_session.return_value = mock_session_manager()
        test_data = {"cpu_load": "45.5", "uptime": "nie_liczba"}

        await save_metrics(device_id=99, data=test_data)

        assert mock_session.add.call_count == 1

    @patch("app.tasks.snmp_collector.get_active_devices")
    @patch("app.tasks.snmp_collector.collect_device_snmp.delay")
    def test_schedule_all_snmp(self, mock_delay, mock_get_devices):
        fake_dev1 = MagicMock(id=1, ip_address="1.1.1.1")
        mock_get_devices.return_value = [fake_dev1]

        schedule_all_snmp()
        assert mock_delay.call_count == 1
        mock_delay.assert_any_call(1, "1.1.1.1")
