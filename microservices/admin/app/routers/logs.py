# routers/logs.py
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from pydantic import UUID4
from models import LogOut, LogListOut

router = APIRouter(prefix="/admin/logs", tags=["Admin Logs"])

# OPTIONAL: gate with an "admin" dependency
async def require_admin():
    # Replace with your auth/role logic; raise if not admin
    return True

@router.get("/", response_model=LogListOut, dependencies=[Depends(require_admin)])
async def list_logs(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user_id: Optional[UUID4] = Query(None),
    level: Optional[str] = Query(None, pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL|AUDIT)$"),
    action_like: Optional[str] = Query(None, description="Search in action (ILIKE)"),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
):
    where = []
    params = []

    if user_id:
        where.append(f"user_id = ${len(params)+1}")
        params.append(str(user_id))
    if level:
        where.append(f"level = ${len(params)+1}")
        params.append(level)
    if action_like:
        where.append(f"action ILIKE ${len(params)+1}")
        params.append(f"%{action_like}%")
    if date_from:
        where.append(f"created_at >= ${len(params)+1}")
        params.append(date_from)
    if date_to:
        where.append(f"created_at <= ${len(params)+1}")
        params.append(date_to)

    where_sql = "WHERE " + " AND ".join(where) if where else ""

    # Count total rows for pagination
    count_sql = f"SELECT COUNT(*) FROM system_log {where_sql}"
    limit = page_size
    offset = (page - 1) * page_size

    async with request.app.state.pool.acquire() as conn:
        total = await conn.fetchval(count_sql, *params)

        rows = await conn.fetch(
            f"""
            SELECT id,
                   user_id,
                   level,
                   action,
                   path,
                   ip::text AS ip,
                   user_agent,
                   meta::json AS meta,
                   created_at
            FROM system_log
            {where_sql}
            ORDER BY created_at DESC
            LIMIT ${len(params)+1} OFFSET ${len(params)+2}
            """,
            *params, limit, offset
        )

    # Ensure meta is always a dict
    import json
    items = []
    for r in rows:
        log = dict(r)
        if isinstance(log.get("meta"), str):
            log["meta"] = json.loads(log["meta"])
        items.append(log)

    pages = (total + page_size - 1) // page_size if total else 0

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages
    }


@router.get("/{log_id}", response_model=LogOut, dependencies=[Depends(require_admin)])
async def get_log(log_id: UUID, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id,
                   user_id,
                   level,
                   action,
                   path,
                   ip::text AS ip,
                   user_agent,
                   meta::json AS meta,
                   created_at
            FROM system_log
            WHERE id = $1
            """,
            str(log_id),
        )

        if not row:
            raise HTTPException(status_code=404, detail="Log not found")

        log = dict(row)

        # Ensure meta is a dict (fix ResponseValidationError)
        if isinstance(log.get("meta"), str):
            import json
            log["meta"] = json.loads(log["meta"])

        return log


@router.delete("/{log_id}", status_code=204, dependencies=[Depends(require_admin)])
async def delete_log(log_id: UUID, request: Request):
    async with request.app.state.pool.acquire() as conn:
        result = await conn.execute("DELETE FROM system_log WHERE id = $1", str(log_id))
        # result like "DELETE 1"
        if result.endswith("0"):
            raise HTTPException(status_code=404, detail="Log not found")
    return
