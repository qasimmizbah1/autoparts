from fastapi import Request, HTTPException

from fastapi import APIRouter, Request
from typing import List

router = APIRouter()

@router.get("/view/")
async def get_makes(request: Request):
    return await get_makes_service(request)


async def get_makes_service(request: Request):
    async with request.app.state.pool.acquire() as conn:
        # Step 1: Fetch all makes
        makes = await conn.fetch("SELECT id, name FROM vehicle_make ORDER BY name")

        all_data = []

        # Step 2: Loop through makes and fetch related models + trims
        for make_row in makes:
            make_id = make_row["id"]

            rows = await conn.fetch("""
                SELECT 
                    vm.id AS model_id,
                    vm.name AS model_name,
                    vm.make_id,
                    vt.id AS trim_id,
                    vt.trim AS trim_name,
                    vt.year_from,
                    vt.year_to
                FROM vehicle_model vm
                LEFT JOIN vehicle_trim vt ON vm.id = vt.model_id
                WHERE vm.make_id = $1
                ORDER BY vm.id, vt.id
            """, make_id)

            # Step 3: Group data into models -> trims
            models = {}
            for row in rows:
                model_id = row["model_id"]
                if model_id not in models:
                    models[model_id] = {
                        "id": str(row["model_id"]),
                        "name": row["model_name"],
                        "make_id": str(row["make_id"]),
                        "trims": []
                    }

                # Append trims if available
                if row["trim_id"]:
                    models[model_id]["trims"].append({
                        "id": str(row["trim_id"]),
                        "make_id": str(row["make_id"]),
                        "model_id": str(row["model_id"]),
                        "trim": row["trim_name"],
                        "year_from": row["year_from"],
                        "year_to": row["year_to"]
                    })

            # Step 4: Combine everything per make
            all_data.append({
                "make_id": str(make_row["id"]),
                "make_name": make_row["name"],
                "models": list(models.values())
            })

        return all_data


from fastapi import HTTPException, Request

async def get_models_service(make_name: str, request: Request):
    async with request.app.state.pool.acquire() as conn:
        # Step 1: Get make_id by name
        make_row = await conn.fetchrow(
            "SELECT id, name FROM vehicle_make WHERE name = $1",
            make_name
        )
        if not make_row:
            raise HTTPException(status_code=404, detail="Make not found")

        make_id = make_row["id"]

        # Step 2: Get all models + trims for this make
        rows = await conn.fetch("""
            SELECT 
                vm.id AS model_id,
                vm.name AS model_name,
                vm.make_id,
                vt.id AS trim_id,
                vt.trim AS trim_name,
                vt.year_from,
                vt.year_to
            FROM vehicle_model vm
            LEFT JOIN vehicle_trim vt ON vm.id = vt.model_id
            WHERE vm.make_id = $1
            ORDER BY vm.id, vt.id
        """, make_id)

        # Step 3: Group data into models -> trims
        models = {}
        for row in rows:
            model_id = row["model_id"]
            if model_id not in models:
                models[model_id] = {
                    "id": str(row["model_id"]),   # convert UUID to str
                    "name": row["model_name"],
                    "make_id": str(row["make_id"]),
                    "trims": []
                }
            if row["trim_id"]:  # append all trims for that model
                models[model_id]["trims"].append({
                    "id": str(row["trim_id"]),
                    "make_id": str(row["make_id"]),
                    "model_id": str(row["model_id"]),
                    "trim": row["trim_name"],
                    "year_from": row["year_from"],
                    "year_to": row["year_to"]
                })

        return {
            "make": make_row["name"],
            "make_id": str(make_row["id"]),
            "models": list(models.values())
        }


async def delete_make_service(make_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        result = await conn.execute("DELETE FROM vehicle_make WHERE id = $1", str(make_id))
        # result like "DELETE 1"
        if result.endswith("0"):
            raise HTTPException(status_code=404, detail="Make not found")
        
    return {"message": "Make deleted successfully"}


async def delete_model_service(model_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        result = await conn.execute("DELETE FROM vehicle_model WHERE id = $1", str(model_id))
        # result like "DELETE 1"
        if result.endswith("0"):
            raise HTTPException(status_code=404, detail="Model not found")
        
    return {"message": "Model deleted successfully"}



async def delete_trim_service(trim_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        result = await conn.execute("DELETE FROM vehicle_trim WHERE id = $1", str(trim_id))
        # result like "DELETE 1"
        if result.endswith("0"):
            raise HTTPException(status_code=404, detail="Trim not found")
        
    return {"message": "Trim deleted successfully"}