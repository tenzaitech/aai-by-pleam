"""
WAWAGOT V.2 Backend API Server
FastAPI-based backend with all WAWAGOT capabilities
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path

# Import WAWAGOT components
try:
    from system.core.controllers.master_controller import master_controller
    from system.core.controllers.chrome_controller import ChromeController
    from system.core.controllers.ai_integration import AIIntegration
    from system.core.controllers.thai_processor import ThaiProcessor
    from system.core.controllers.knowledge_manager import KnowledgeManager
    from system.core.controllers.visual_recognition import VisualRecognition
except ImportError:
    # Mock classes for development/testing
    class MockMasterController:
        def __init__(self):
            self.is_initialized = True
            self.chrome_controller = MockChromeController()
            self.ai_integration = MockAIIntegration()
            self.thai_processor = MockThaiProcessor()
            self.knowledge_manager = MockKnowledgeManager()
            self.visual_recognition = MockVisualRecognition()
        
        def initialize_system(self):
            return True
        
        def shutdown_system(self):
            pass
        
        def get_system_status(self):
            return {
                "chrome": "ready",
                "ai": "ready", 
                "thai_processor": "ready",
                "knowledge_manager": "ready",
                "visual_recognition": "ready"
            }
    
    class MockChromeController:
        async def navigate_to(self, url):
            return {"status": "success", "url": url}
        
        async def click_element(self, selector):
            return {"status": "success", "selector": selector}
        
        async def type_text(self, selector, text):
            return {"status": "success", "selector": selector, "text": text}
        
        async def take_screenshot(self):
            return {"status": "success", "screenshot": "mock_screenshot.png"}
        
        async def scroll_page(self, direction):
            return {"status": "success", "direction": direction}
    
    class MockAIIntegration:
        async def process_command(self, command, parameters):
            return {"status": "success", "command": command, "response": "Mock AI response"}
        
        async def process_with_vision(self, prompt, image_data):
            return {"status": "success", "prompt": prompt, "response": "Mock vision response"}
    
    class MockThaiProcessor:
        async def process_command(self, command, parameters):
            return {"status": "success", "command": command, "response": "Mock Thai response"}
    
    class MockKnowledgeManager:
        async def store_knowledge(self, data):
            return {"status": "success", "stored": data}
        
        async def retrieve_knowledge(self, query):
            return {"status": "success", "query": query, "results": ["Mock knowledge"]}
    
    class MockVisualRecognition:
        async def analyze_image(self, image_data):
            return {"status": "success", "analysis": "Mock image analysis"}
    
    # Use mock instances
    master_controller = MockMasterController()
    ChromeController = MockChromeController
    AIIntegration = MockAIIntegration
    ThaiProcessor = MockThaiProcessor
    KnowledgeManager = MockKnowledgeManager
    VisualRecognition = MockVisualRecognition

# Initialize FastAPI app
app = FastAPI(
    title="WAWAGOT V.2 API",
    description="AI-Powered Chrome Automation System API",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global system instance
system = None

class CommandRequest(BaseModel):
    command: str
    parameters: Optional[Dict[str, Any]] = {}
    language: str = "thai"

class AIRequest(BaseModel):
    prompt: str
    context: Optional[str] = ""
    use_vision: bool = False

class ChromeRequest(BaseModel):
    url: Optional[str] = None
    action: str
    parameters: Optional[Dict[str, Any]] = {}

class SystemConfig(BaseModel):
    chrome_headless: bool = False
    ai_enabled: bool = True
    thai_processing: bool = True
    parallel_processing: bool = True

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    global system
    try:
        # Initialize master controller
        system = master_controller
        success = system.initialize_system()
        
        if success:
            logging.info("✅ WAWAGOT V.2 Backend initialized successfully")
        else:
            logging.error("❌ Failed to initialize WAWAGOT V.2 Backend")
            
    except Exception as e:
        logging.error(f"❌ Startup error: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global system
    if system:
        system.shutdown_system()
        logging.info("🔄 WAWAGOT V.2 Backend shutdown complete")

# Health Check
@app.get("/")
async def root():
    return {
        "message": "WAWAGOT V.2 API Server",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """System health check"""
    global system
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    status = system.get_system_status()
    return {
        "status": "healthy" if system.is_initialized else "unhealthy",
        "components": status,
        "timestamp": datetime.now().isoformat()
    }

# AI Command Processing
@app.post("/api/command")
async def process_command(request: CommandRequest, background_tasks: BackgroundTasks):
    """Process AI commands in natural language"""
    global system
    if not system or not system.is_initialized:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Process command based on language
        if request.language == "thai":
            # Use Thai processor
            result = await system.thai_processor.process_command(
                request.command, 
                request.parameters
            )
        else:
            # Use AI integration for English
            result = await system.ai_integration.process_command(
                request.command,
                request.parameters
            )
        
        return {
            "success": True,
            "command": request.command,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Command processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chrome Control API
@app.post("/api/chrome")
async def chrome_control(request: ChromeRequest):
    """Control Chrome browser"""
    global system
    if not system or not system.chrome_controller:
        raise HTTPException(status_code=503, detail="Chrome controller not available")
    
    try:
        chrome = system.chrome_controller
        
        if request.action == "navigate":
            result = await chrome.navigate_to(request.url)
        elif request.action == "click":
            result = await chrome.click_element(request.parameters.get("selector"))
        elif request.action == "type":
            result = await chrome.type_text(
                request.parameters.get("selector"),
                request.parameters.get("text")
            )
        elif request.action == "screenshot":
            result = await chrome.take_screenshot()
        elif request.action == "scroll":
            result = await chrome.scroll_page(request.parameters.get("direction", "down"))
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")
        
        return {
            "success": True,
            "action": request.action,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Chrome control error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# AI Integration API
@app.post("/api/ai")
async def ai_processing(request: AIRequest):
    """AI processing with OpenAI"""
    global system
    if not system or not system.ai_integration:
        raise HTTPException(status_code=503, detail="AI integration not available")
    
    try:
        ai = system.ai_integration
        
        if request.use_vision:
            # Use vision model
            result = await ai.process_with_vision(request.prompt, request.context)
        else:
            # Use text model
            result = await ai.process_text(request.prompt, request.context)
        
        return {
            "success": True,
            "prompt": request.prompt,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"AI processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Visual Recognition API
@app.post("/api/visual")
async def visual_recognition(image_data: str):
    """Visual recognition and OCR"""
    global system
    if not system or not system.visual_recognition:
        raise HTTPException(status_code=503, detail="Visual recognition not available")
    
    try:
        visual = system.visual_recognition
        result = await visual.analyze_image(image_data)
        
        return {
            "success": True,
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Visual recognition error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Knowledge Management API
@app.get("/api/knowledge")
async def get_knowledge(query: str = ""):
    """Retrieve knowledge from database"""
    global system
    if not system or not system.knowledge_manager:
        raise HTTPException(status_code=503, detail="Knowledge manager not available")
    
    try:
        km = system.knowledge_manager
        if query:
            result = await km.search_knowledge(query)
        else:
            result = await km.get_all_knowledge()
        
        return {
            "success": True,
            "query": query,
            "results": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Knowledge retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/knowledge")
async def store_knowledge(data: Dict[str, Any]):
    """Store knowledge in database"""
    global system
    if not system or not system.knowledge_manager:
        raise HTTPException(status_code=503, detail="Knowledge manager not available")
    
    try:
        km = system.knowledge_manager
        result = await km.store_knowledge(data)
        
        return {
            "success": True,
            "stored": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Knowledge storage error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System Configuration API
@app.get("/api/config")
async def get_config():
    """Get system configuration"""
    global system
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        config = system.config_manager.get_config() if hasattr(system, 'config_manager') else {}
        return {
            "success": True,
            "config": config,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Config retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/config")
async def update_config(config: SystemConfig):
    """Update system configuration"""
    global system
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        # Update configuration
        if hasattr(system, 'config_manager'):
            system.config_manager.update_config(config.dict())
        
        return {
            "success": True,
            "message": "Configuration updated",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Config update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System Control API
@app.post("/api/system/restart")
async def restart_system():
    """Restart the entire system"""
    global system
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        success = system.restart_system()
        return {
            "success": success,
            "message": "System restarted" if success else "Restart failed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"System restart error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/system/shutdown")
async def shutdown_system():
    """Shutdown the system"""
    global system
    if not system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        success = system.shutdown_system()
        return {
            "success": success,
            "message": "System shutdown" if success else "Shutdown failed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"System shutdown error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 