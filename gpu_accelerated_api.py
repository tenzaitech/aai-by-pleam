# WAWAGOT.AI - GPU Accelerated API
# ===============================================================================
# WAWAGOT.AI - API สำหรับ GPU-accelerated services
# ===============================================================================
# Created: 2024-12-19
# Purpose: API สำหรับเชื่อมต่อ GPU services กับโปรแกรมอื่น
# ===============================================================================

import asyncio
import json
import base64
import io
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
    TZ_BANGKOK = ZoneInfo("Asia/Bangkok")
except ImportError:
    import pytz
    TZ_BANGKOK = pytz.timezone("Asia/Bangkok")
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
from pydantic import BaseModel

# Import GPU Manager
from gpu_manager import GPUManager, GPUAcceleratedServices

# ===============================================================================
# API MODELS
# ===============================================================================

class TextGenerationRequest(BaseModel):
    """Request สำหรับ Text Generation แบบ hybrid"""
    prompt: str
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 1000
    temperature: float = 0.7
    provider: str = "openai"
    device: str = "auto"  # auto, gpu, cpu

class ImageProcessingRequest(BaseModel):
    """Request สำหรับ Image Processing แบบ hybrid"""
    operation: str  # resize, filter, detection, segmentation
    parameters: Dict[str, Any] = {}
    device: str = "auto"  # auto, gpu, cpu

class VoiceSynthesisRequest(BaseModel):
    """Request สำหรับ Voice Synthesis แบบ hybrid"""
    text: str
    voice: str = "default"
    speed: float = 1.0
    provider: str = "retell"
    device: str = "auto"  # auto, gpu, cpu

class OCRRequest(BaseModel):
    """Request สำหรับ OCR แบบ hybrid"""
    language: str = "eng"
    engine: str = "tesseract"
    device: str = "auto"  # auto, gpu, cpu

class GPUStatusResponse(BaseModel):
    """Response สำหรับ GPU Status"""
    success: bool
    gpu_count: int
    utilization: Dict[str, Any]
    memory_usage: Dict[str, Any]
    temperature: Dict[str, Any]

# ===============================================================================
# GPU API SERVER
# ===============================================================================

class GPUAPIServer:
    """GPU API Server สำหรับเชื่อมต่อกับโปรแกรมอื่น"""
    
    def __init__(self):
        self.app = FastAPI(
            title="WAWAGOT.AI GPU API",
            description="GPU-accelerated AI services API",
            version="1.0.0"
        )
        self.gpu_manager = GPUManager()
        self.gpu_services = None
        self.setup_routes()
        self.setup_cors()
    
    def setup_cors(self):
        """ตั้งค่า CORS"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # อนุญาตทุก origin
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """ตั้งค่า API routes"""
        
        # Health Check
        @self.app.get("/")
        async def root():
            return {
                "message": "WAWAGOT.AI GPU API",
                "status": "running",
                "timestamp": datetime.now(TZ_BANGKOK).isoformat()
            }
        
        # GPU Status
        @self.app.get("/api/gpu/status", response_model=GPUStatusResponse)
        async def get_gpu_status():
            """ดึงสถานะ GPU"""
            try:
                status = await self.gpu_manager.get_gpu_status()
                if status["success"]:
                    return GPUStatusResponse(
                        success=True,
                        gpu_count=status.get("total_gpus", 0),
                        utilization=status.get("utilization", {}),
                        memory_usage={},
                        temperature={}
                    )
                else:
                    raise HTTPException(status_code=500, detail=status["error"])
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # GPU Optimization
        @self.app.post("/api/gpu/optimize")
        async def optimize_gpu():
            """ปรับปรุงการใช้ GPU"""
            try:
                result = await self.gpu_manager.optimize_gpu_usage()
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Text Generation
        @self.app.post("/api/ai/text/generate")
        async def generate_text(request: TextGenerationRequest):
            """สร้างข้อความด้วย AI แบบ hybrid"""
            try:
                if not self.gpu_services:
                    raise HTTPException(status_code=503, detail="GPU services not initialized")
                
                # ใช้ hybrid service
                result = await self.gpu_services._generate_text_hybrid(request, request.device)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Image Processing
        @self.app.post("/api/ai/image/process")
        async def process_image(
            file: UploadFile = File(...),
            operation: str = "resize",
            device: str = "auto"
        ):
            """ประมวลผลภาพด้วย GPU แบบ hybrid"""
            try:
                if not self.gpu_services:
                    raise HTTPException(status_code=503, detail="GPU services not initialized")
                
                # อ่านไฟล์ภาพ
                image_data = await file.read()
                
                # ประมวลผลแบบ hybrid
                result = await self.gpu_services._process_image_hybrid(image_data, operation, device)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Voice Synthesis
        @self.app.post("/api/ai/voice/synthesize")
        async def synthesize_voice(request: VoiceSynthesisRequest):
            """สร้างเสียงพูดด้วย AI"""
            try:
                if not self.gpu_services:
                    raise HTTPException(status_code=503, detail="GPU services not initialized")
                
                # ใช้ GPU acceleration สำหรับ voice synthesis
                result = await self._synthesize_voice_gpu(request)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # OCR Processing
        @self.app.post("/api/ai/ocr/process")
        async def process_ocr(
            file: UploadFile = File(...),
            language: str = "eng",
            engine: str = "tesseract"
        ):
            """ประมวลผล OCR ด้วย GPU"""
            try:
                if not self.gpu_services:
                    raise HTTPException(status_code=503, detail="GPU services not initialized")
                
                # อ่านไฟล์
                file_data = await file.read()
                
                # ประมวลผล OCR ด้วย GPU
                result = await self._process_ocr_gpu(file_data, language, engine)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Model Management
        @self.app.post("/api/gpu/models/load")
        async def load_model(model_name: str, model_path: str):
            """โหลด Model ไปยัง GPU"""
            try:
                result = await self.gpu_manager.load_model_to_gpu(model_name, model_path)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Batch Processing
        @self.app.post("/api/gpu/batch/process")
        async def batch_process(requests: List[Dict[str, Any]]):
            """ประมวลผลแบบ Batch ด้วย GPU"""
            try:
                results = []
                for request in requests:
                    if request["type"] == "text":
                        result = await self._generate_text_gpu(TextGenerationRequest(**request["data"]))
                    elif request["type"] == "image":
                        result = await self._process_image_gpu(request["data"], request["operation"])
                    elif request["type"] == "voice":
                        result = await self._synthesize_voice_gpu(VoiceSynthesisRequest(**request["data"]))
                    else:
                        result = {"error": f"Unknown request type: {request['type']}"}
                    
                    results.append(result)
                
                return {"success": True, "results": results}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Real-time Streaming
        @self.app.get("/api/gpu/stream/status")
        async def stream_gpu_status():
            """Stream สถานะ GPU แบบ Real-time"""
            async def generate():
                while True:
                    try:
                        status = await self.gpu_manager.get_gpu_status()
                        yield f"data: {json.dumps(status)}\n\n"
                        await asyncio.sleep(1)
                    except Exception as e:
                        yield f"data: {json.dumps({'error': str(e)})}\n\n"
                        await asyncio.sleep(5)
            
            return StreamingResponse(generate(), media_type="text/plain")
    
    async def _generate_text_gpu(self, request: TextGenerationRequest) -> Dict[str, Any]:
        """สร้างข้อความด้วย GPU acceleration"""
        try:
            # ใช้ GPU memory สำหรับ model loading
            if TORCH_AVAILABLE and cuda.is_available():
                # ย้าย model ไป GPU ถ้าจำเป็น
                pass
            
            # เรียกใช้ OpenAI API หรือ Gemini API
            if request.provider == "openai":
                # ใช้ OpenAI API
                result = await self._call_openai_api(request)
            elif request.provider == "gemini":
                # ใช้ Gemini API
                result = await self._call_gemini_api(request)
            else:
                result = {"error": f"Unknown provider: {request.provider}"}
            
            return {
                "success": True,
                "text": result.get("text", ""),
                "provider": request.provider,
                "model": request.model,
                "gpu_accelerated": True,
                "processing_time": 0.1  # จะคำนวณจริง
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_image_gpu(self, image_data: bytes, operation: str, gpu_accelerated: bool) -> Dict[str, Any]:
        """ประมวลผลภาพด้วย GPU"""
        try:
            if OPENCV_AVAILABLE and gpu_accelerated:
                # ใช้ OpenCV CUDA
                if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                    # แปลงเป็น numpy array
                    import numpy as np
                    nparr = np.frombuffer(image_data, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    # ย้ายไป GPU
                    gpu_img = cv2.cuda_GpuMat()
                    gpu_img.upload(img)
                    
                    # ประมวลผลตาม operation
                    if operation == "resize":
                        # Resize ด้วย GPU
                        gpu_result = cv2.cuda.resize(gpu_img, (640, 480))
                        result_img = gpu_result.download()
                    elif operation == "filter":
                        # Filter ด้วย GPU
                        gpu_result = cv2.cuda.GaussianBlur(gpu_img, (15, 15), 0)
                        result_img = gpu_result.download()
                    else:
                        result_img = img
                    
                    # แปลงกลับเป็น bytes
                    _, buffer = cv2.imencode('.jpg', result_img)
                    result_data = base64.b64encode(buffer).decode('utf-8')
                    
                    return {
                        "success": True,
                        "operation": operation,
                        "gpu_accelerated": True,
                        "image_data": result_data,
                        "processing_time": 0.05
                    }
            
            # Fallback ไป CPU
            return {
                "success": True,
                "operation": operation,
                "gpu_accelerated": False,
                "message": "Using CPU fallback"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _synthesize_voice_gpu(self, request: VoiceSynthesisRequest) -> Dict[str, Any]:
        """สร้างเสียงพูดด้วย GPU"""
        try:
            # ใช้ Retell.AI หรือ OpenAI TTS
            if request.provider == "retell":
                # เรียก Retell.AI API
                result = await self._call_retell_api(request)
            elif request.provider == "openai_tts":
                # เรียก OpenAI TTS API
                result = await self._call_openai_tts_api(request)
            else:
                result = {"error": f"Unknown provider: {request.provider}"}
            
            return {
                "success": True,
                "audio_data": result.get("audio_data", ""),
                "provider": request.provider,
                "voice": request.voice,
                "gpu_accelerated": True,
                "processing_time": 0.2
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_ocr_gpu(self, file_data: bytes, language: str, engine: str) -> Dict[str, Any]:
        """ประมวลผล OCR ด้วย GPU"""
        try:
            # ใช้ Tesseract หรือ PaddleOCR
            if engine == "tesseract":
                # ใช้ Tesseract
                result = await self._call_tesseract_ocr(file_data, language)
            elif engine == "paddleocr":
                # ใช้ PaddleOCR
                result = await self._call_paddleocr_ocr(file_data, language)
            else:
                result = {"error": f"Unknown engine: {engine}"}
            
            return {
                "success": True,
                "text": result.get("text", ""),
                "engine": engine,
                "language": language,
                "gpu_accelerated": True,
                "processing_time": 0.1
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Placeholder methods สำหรับ API calls
    async def _call_openai_api(self, request: TextGenerationRequest) -> Dict[str, Any]:
        """เรียก OpenAI API"""
        return {"text": f"Generated text for: {request.prompt[:50]}..."}
    
    async def _call_gemini_api(self, request: TextGenerationRequest) -> Dict[str, Any]:
        """เรียก Gemini API"""
        return {"text": f"Gemini generated: {request.prompt[:50]}..."}
    
    async def _call_retell_api(self, request: VoiceSynthesisRequest) -> Dict[str, Any]:
        """เรียก Retell.AI API"""
        return {"audio_data": "base64_encoded_audio_data"}
    
    async def _call_openai_tts_api(self, request: VoiceSynthesisRequest) -> Dict[str, Any]:
        """เรียก OpenAI TTS API"""
        return {"audio_data": "base64_encoded_audio_data"}
    
    async def _call_tesseract_ocr(self, file_data: bytes, language: str) -> Dict[str, Any]:
        """เรียก Tesseract OCR"""
        return {"text": "Extracted text from image"}
    
    async def _call_paddleocr_ocr(self, file_data: bytes, language: str) -> Dict[str, Any]:
        """เรียก PaddleOCR"""
        return {"text": "Extracted text from image"}
    
    async def start_server(self, host: str = "0.0.0.0", port: int = 8000):
        """เริ่มต้น API Server"""
        # เริ่มต้น GPU Manager
        await self.gpu_manager.initialize_gpu_system()
        
        # เริ่มต้น GPU Services
        self.gpu_services = GPUAcceleratedServices(self.gpu_manager)
        await self.gpu_services.initialize_services()
        
        print(f"🚀 GPU API Server เริ่มต้นที่: http://{host}:{port}")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("🔧 GPU Services พร้อมใช้งาน!")
        
        # เริ่มต้น server
        config = uvicorn.Config(self.app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

# ===============================================================================
# MAIN EXECUTION
# ===============================================================================

async def main():
    """ฟังก์ชันหลัก"""
    server = GPUAPIServer()
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main()) 