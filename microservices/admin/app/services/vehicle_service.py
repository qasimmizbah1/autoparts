from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRequest, BuyerUpdate, SupplierUpdate, VehicleMake, VehicleModel, VehicleTrim
from uuid import UUID, uuid4
from deps import require_admin

#vechile Make

async def add_make_service(make, request: Request):
    async with request.app.state.pool.acquire() as conn:
        try:
            result = await conn.fetchrow(
                "INSERT INTO vehicle_make (id, name) VALUES ($1, $2) RETURNING *",
                uuid4(), make.name
            )
            return dict(result)
        except Exception:
            raise HTTPException(status_code=400, detail="Make already exists")


async def update_make_service(make_id, make, request: Request):
    async with request.app.state.pool.acquire() as conn:
        # Check if the new name already exists for a different make
        existing = await conn.fetchrow(
            "SELECT id FROM vehicle_make WHERE name=$1 AND id!=$2",
            make.name, make_id
        )
        if existing:
            raise HTTPException(status_code=400, detail="Make name already exists")

        # Perform the update
        result = await conn.execute(
            "UPDATE vehicle_make SET name=$1 WHERE id=$2",
            make.name, make_id
        )

        # Check if update actually happened
        if result[-1] == "0":
            raise HTTPException(status_code=404, detail="Make not found")

        return {"status": "updated"}



async def add_model_service(model, request: Request):
    async with request.app.state.pool.acquire() as conn:
        try:
            result = await conn.fetchrow(
                "INSERT INTO vehicle_model (id, make_id, name) VALUES ($1, $2, $3) RETURNING *",
                uuid4(), model.make_id, model.name
            )
            return dict(result)
        except Exception:
            raise HTTPException(status_code=400, detail="Model already exists for this make")
        


async def update_model_service(model_id, model, request: Request):
    async with request.app.state.pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE vehicle_model SET name=$1 WHERE id=$2",
            model.name, model_id
        )
        if result[-1] == "0":
            raise HTTPException(status_code=404, detail="Model not found")
        return {"status": "updated"}
    


async def add_trim_service(trim, request: Request):
    async with request.app.state.pool.acquire() as conn:
        try:
            result = await conn.fetchrow(
                "INSERT INTO vehicle_trim (id, make_id, model_id, year_from, year_to, trim) VALUES ($1, $2, $3, $4, $5, $6) RETURNING *",
                uuid4(), trim.make_id, trim.model_id, trim.year_from, trim.year_to, trim.trim
            )
            return dict(result)
        except Exception:
            raise HTTPException(status_code=400, detail="Trim already exists for this model")
        

async def update_trim_service(trim_id, trim, request: Request):
    async with request.app.state.pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE vehicle_trim SET make_id=$1,model_id=$2,year_from=$3, year_to=$4, trim=$5 WHERE id=$6",
            trim.make_id,trim.model_id,trim.year_from, trim.year_to, trim.trim, trim_id
        )
        if result[-1] == "0":
            raise HTTPException(status_code=404, detail="Trim not found")
        return {"status": "updated"}
    