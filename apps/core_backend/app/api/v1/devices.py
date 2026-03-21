from app.api.dependencies import get_current_user, require_role
from app.db.deps import SessionPG
from app.models.user import User, UserRole
from app.schemas.devices import DevicePut
from app.services.device_services import DeviceService
from fastapi import APIRouter, Depends, Response

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])


# Dependency to inject the service
def get_device_service(session: SessionPG) -> DeviceService:
    return DeviceService(session)


@router.get("/")
async def list_devices(
    service: DeviceService = Depends(get_device_service),
    _: User = Depends(
        require_role(
            [UserRole.ADMIN, UserRole.OPERATOR, UserRole.READONLY, UserRole.AUDITOR]
        )
    ),
):
    return await service.get_all()


@router.post("/", status_code=201)
async def add_device(
    payload: DevicePut,
    service: DeviceService = Depends(get_device_service),
    _: User = Depends(require_role([UserRole.ADMIN])),
):
    return await service.create(payload.model_dump())


@router.get("/{id}")
async def read_device(
    id: int,
    service: DeviceService = Depends(get_device_service),
    _: User = Depends(
        require_role(
            [UserRole.ADMIN, UserRole.OPERATOR, UserRole.READONLY, UserRole.AUDITOR]
        )
    ),
):
    return await service.get_by_id(id)


@router.put("/{id}")
async def update_device(
    id: int,
    payload: DevicePut,
    service: DeviceService = Depends(get_device_service),
    _: User = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR])),
):
    return await service.update(id, payload.model_dump())


@router.delete("/{id}")
async def soft_delete_device(
    id: int,
    service: DeviceService = Depends(get_device_service),
    _: User = Depends(require_role([UserRole.ADMIN])),
):
    await service.soft_delete(id)
    return Response(status_code=200, content="Device deleted successfully")
