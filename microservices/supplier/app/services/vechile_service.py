from fastapi import Request

async def get_makes_service(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM vehicle_make")
        return [dict(r) for r in rows]

    
async def get_models_service(make_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM vehicle_model WHERE make_id = $1",
            make_id
        )
        return [dict(r) for r in rows]
    

async def get_trims_service(model_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM vehicle_trim WHERE model_id = $1",
            model_id
        )
        return [dict(r) for r in rows]