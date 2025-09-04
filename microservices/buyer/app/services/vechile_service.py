from fastapi import Request

async def get_makes_service(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM vehicle_make")
        return [dict(r) for r in rows]
    

async def get_models_service(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM vehicle_model")
        return [dict(r) for r in rows]
    

async def get_trims_service(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM vehicle_trim")
        return [dict(r) for r in rows]