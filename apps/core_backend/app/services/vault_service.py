import hvac
import hvac.exceptions
from app.core.config import Config
from app.models.device import Credential
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

_MOUNT = "secret"


def _build_path(device_id: int, credential_type: str) -> str:
    """KV v2 path (without mount prefix)."""
    return f"devices/{device_id}/{credential_type}"


def _full_path(device_id: int, credential_type: str) -> str:
    """Full path stored in the Credential table."""
    return f"{_MOUNT}/data/{_build_path(device_id, credential_type)}"


class VaultService:
    def __init__(self, session: AsyncSession):
        self.client = hvac.Client(
            url=Config.VAULT_ADDR,
            token=Config.VAULT_TOKEN,
        )
        self.session = session

    def _check_connection(self) -> None:
        """Raise 503 if Vault is unreachable or the token is invalid."""
        try:
            authenticated = self.client.is_authenticated()
        except Exception as exc:
            raise HTTPException(503, f"Cannot reach Vault: {exc}") from exc

        if not authenticated:
            raise HTTPException(503, "Vault token is invalid or expired")

    async def _upsert_credential(
        self, device_id: int, credential_type: str, vault_path: str
    ) -> None:
        """Create or update the Credential row in PostgreSQL."""
        result = await self.session.execute(
            select(Credential).where(
                Credential.device_id == device_id,
                Credential.credential_type == credential_type,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.vault_path = vault_path
        else:
            self.session.add(
                Credential(
                    device_id=device_id,
                    credential_type=credential_type,
                    vault_path=vault_path,
                )
            )
        await self.session.commit()

    async def set_device_credentials(
        self, device_id: int, credential_type: str, credentials: dict
    ) -> str:
        """
        Write *credentials* to Vault and persist the path in PostgreSQL.
        Returns the full Vault path stored in the Credential table.
        """
        self._check_connection()

        path = _build_path(device_id, credential_type)
        stored_path = _full_path(device_id, credential_type)

        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=credentials,
                mount_point=_MOUNT,
            )
        except hvac.exceptions.VaultError as exc:
            raise HTTPException(503, f"Vault write failed: {exc}") from exc

        await self._upsert_credential(device_id, credential_type, stored_path)
        return stored_path

    async def get_device_credentials(
        self, device_id: int, credential_type: str
    ) -> dict:
        """
        Retrieve credentials by looking up the Vault path from PostgreSQL,
        then reading the secret from Vault.
        """
        self._check_connection()

        # 1. Resolve the Vault path from the Credential table
        result = await self.session.execute(
            select(Credential).where(
                Credential.device_id == device_id,
                Credential.credential_type == credential_type,
            )
        )
        credential = result.scalar_one_or_none()

        if not credential:
            raise HTTPException(
                404,
                f"No '{credential_type}' credentials found for device {device_id}",
            )

        # 2. Strip mount prefix to get the KV v2 path
        clean_path = credential.vault_path.removeprefix(f"{_MOUNT}/data/")

        # 3. Read from Vault
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=clean_path,
                mount_point=_MOUNT,
            )
            return response["data"]["data"]
        except hvac.exceptions.InvalidPath as exc:
            raise HTTPException(
                404,
                f"Secret not found in Vault at: {credential.vault_path}",
            ) from exc
        except hvac.exceptions.VaultError as exc:
            raise HTTPException(503, f"Vault read failed: {exc}") from exc

    async def delete_device_credentials(
        self, device_id: int, credential_type: str
    ) -> None:
        """
        Soft-delete the secret in Vault and remove the Credential row.
        Called when a device is permanently removed (not used for soft-delete).
        """
        self._check_connection()

        result = await self.session.execute(
            select(Credential).where(
                Credential.device_id == device_id,
                Credential.credential_type == credential_type,
            )
        )
        credential = result.scalar_one_or_none()

        if not credential:
            return  # Nothing to remove

        clean_path = credential.vault_path.removeprefix(f"{_MOUNT}/data/")

        try:
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=clean_path,
                mount_point=_MOUNT,
            )
        except hvac.exceptions.InvalidPath:
            pass  # Already gone from Vault — still clean up the DB row
        except hvac.exceptions.VaultError as exc:
            raise HTTPException(503, f"Vault delete failed: {exc}") from exc

        await self.session.delete(credential)
        await self.session.commit()
