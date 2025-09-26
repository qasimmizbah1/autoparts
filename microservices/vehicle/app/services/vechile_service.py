from fastapi import Request, HTTPException

async def get_makes_service(request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM vehicle_make")
        return [dict(r) for r in rows]


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
            raise HTTPException(status_code=404, detail="User not found")
        
    return {"message": "User and related profiles deleted successfully"}