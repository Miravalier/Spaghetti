from fastapi import APIRouter


router = APIRouter()


@router.put("/net-worth")
async def put_net_worth():
    return {"balance": 0.0}


@router.put("/authstatus")
async def put_auth_status():
    return {"status": "authenticated", "user": "none@example.com"}


@router.put("/status")
async def put_status():
    return {"status": "online"}


@router.get("/status")
async def get_status():
    return {"status": "online"}


@router.put("/list-users")
async def list_users():
    return {"users": [[1, "Update This App"]]}


@router.put("/transfer/list-inbound")
async def list_inbound():
    return {"requests": []}


@router.put("/transfer/list-outbound")
async def list_outbound():
    return {"requests": []}


@router.put("/transfer/deny")
async def deny_transfer():
    return {"success": "Request denied."}


@router.put("/transfer/accept")
async def accept_transfer():
    return {"success": "Request accepted."}


@router.put("/transfer/create")
async def create_transfer():
    return {"success": "Transfer requested."}


@router.put("/update-username")
async def update_username():
    return {"success": "Username updated."}
