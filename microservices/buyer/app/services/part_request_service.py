from fastapi import Request, UploadFile, APIRouter, Form, File, HTTPException
from uuid import UUID, uuid4
from models import VehicleMake, VehicleModel, VehicleTrim
from services.vechile_service import get_makes_service, get_models_service, get_trims_service
from typing import Optional, List
from models import PartRequest, PartRequestInDB
from datetime import date
import os


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


#Create part resquset 
async def create_part_request_service(request,user_id,title,urgency,vehicle_make,vehicle_model,vehicle_model_trim,required_by_date,description,attachment):

    filename = attachment.filename if attachment else None

    if attachment:
            filename = f"{user_id}_{attachment.filename}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(await attachment.read())

    async with request.app.state.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO part_request
                (user_id, title, description, urgency, required_by_date, 
                vehicle_make, vehicle_model, vehicle_model_trim, attachment)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id, user_id, title, description, urgency, required_by_date,
                        vehicle_make, vehicle_model, vehicle_model_trim, attachment,
                        created_at, updated_at
                """,
                user_id, title, description, urgency, required_by_date,
                vehicle_make, vehicle_model, vehicle_model_trim, filename
            )

    return dict(row)


#update part resquset 
async def update_part_request_service(request,part_request_id,title,urgency,vehicle_make,vehicle_model,vehicle_model_trim,required_by_date,description,attachment,):
    
    filename = None

    if attachment:
        filename = f"{part_request_id}_{attachment.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(await attachment.read())

    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            UPDATE part_request
            SET 
                title = COALESCE($2, title),
                description = COALESCE($3, description),
                urgency = COALESCE($4, urgency),
                required_by_date = COALESCE($5, required_by_date),
                vehicle_make = COALESCE($6, vehicle_make),
                vehicle_model = COALESCE($7, vehicle_model),
                vehicle_model_trim = COALESCE($8, vehicle_model_trim),
                attachment = COALESCE($9, attachment),
                updated_at = NOW()
            WHERE id = $1
            RETURNING id, user_id, title, description, urgency, required_by_date,
                      vehicle_make, vehicle_model, vehicle_model_trim, attachment,
                      created_at, updated_at
            """,
            part_request_id,
            title,
            description,
            urgency,
            required_by_date,
            vehicle_make,
            vehicle_model,
            vehicle_model_trim,
            filename,
        )

        if not row:
            raise HTTPException(status_code=404, detail="Part request not found")

    return dict(row)


#view by user_id
async def get_all_parts_request_service(user_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM part_request WHERE user_id = $1",
            user_id
        )
        return [dict(r) for r in rows]

#view by id
async def get_parts_request_service(part_request_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT * FROM part_request WHERE id = $1",
            part_request_id
        )
        return [dict(r) for r in rows]

#delete request  
async def delete_parts_request_service(part_request_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch(
            "delete FROM part_request WHERE id = $1 RETURNING *",
            part_request_id
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Part request not found")
        
        return [dict(r) for r in rows]
            


