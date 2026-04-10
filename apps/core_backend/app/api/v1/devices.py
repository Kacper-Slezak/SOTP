from app.api.dependencies import get_current_user, require_role
from app.db.deps import SessionPG
from app.models.user import User, UserRole
from app.schemas.devices import DeviceOut, DevicePut, PaginatedResponse
from app.services.device_services import DeviceService, SortOrder
from fastapi import APIRouter, Depends, Query, Response

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])


# Dependency to inject the service
def get_device_service(session: SessionPG) -> DeviceService:
    return DeviceService(session)


@router.get("/", response_model=PaginatedResponse[DeviceOut])
async def list_devices(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    sort_by: str = Query(default="id"),
    sort_order: SortOrder = Query(default=SortOrder.asc),
    is_active: bool | None = Query(default=None),
    device_type: str | None = Query(default=None),
    vendor: str | None = Query(default=None),
    service: DeviceService = Depends(get_device_service),
    _: User = Depends(
        require_role(
            [UserRole.ADMIN, UserRole.OPERATOR, UserRole.READONLY, UserRole.AUDITOR]
        )
    ),
):
    items, total = await service.get_all(
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
        is_active=is_active,
        device_type=device_type,
        vendor=vendor,
    )
    return PaginatedResponse(items=items, total_count=total, limit=limit, offset=offset)


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
