from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Dict, Any
import json
import os
from datetime import datetime

from app.models.chat import BotConfig, CompanyData
from app.schemas.common import DataResponse

router = APIRouter()
security = HTTPBasic()

# Simple admin auth (bisa diganti dengan JWT)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != ADMIN_USERNAME or credentials.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials

@router.get("/data", response_model=DataResponse[Dict[str, Any]])
async def get_current_data(admin: HTTPBasicCredentials = Depends(verify_admin)):
    """Get current data.json content"""
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return DataResponse(
            success=True,
            message="Data retrieved successfully",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data", response_model=DataResponse[None])
async def update_data(
    data: Dict[str, Any],
    admin: HTTPBasicCredentials = Depends(verify_admin)
):
    """Update data.json content"""
    try:
        # Validate structure
        BotConfig(**data.get("bot_config", {}))
        CompanyData(**data.get("company_data", {}))
        
        # Backup current data
        backup_filename = f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open("data.json", "r", encoding="utf-8") as f:
            backup_data = json.load(f)
        with open(f"backups/{backup_filename}", "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        # Update data.json
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Trigger reload
        from app.api.v1.endpoints.chat import chatbot_service
        chatbot_service._load_data()
        await chatbot_service.initialize_embeddings()
        
        return DataResponse(
            success=True,
            message="Data updated successfully",
            data=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/bot-config", response_model=DataResponse[None])
async def update_bot_config(
    config: BotConfig,
    admin: HTTPBasicCredentials = Depends(verify_admin)
):
    """Update bot configuration only"""
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        data["bot_config"] = config.dict()
        
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Trigger reload
        from app.api.v1.endpoints.chat import chatbot_service
        chatbot_service._load_data()
        
        return DataResponse(
            success=True,
            message="Bot configuration updated successfully",
            data=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backups", response_model=DataResponse[list])
async def list_backups(admin: HTTPBasicCredentials = Depends(verify_admin)):
    """List available backups"""
    try:
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        backups = []
        for filename in os.listdir(backup_dir):
            if filename.startswith("data_backup_") and filename.endswith(".json"):
                file_path = os.path.join(backup_dir, filename)
                stat = os.stat(file_path)
                backups.append({
                    "filename": filename,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "size": stat.st_size
                })
        
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return DataResponse(
            success=True,
            message="Backups retrieved successfully",
            data=backups
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))