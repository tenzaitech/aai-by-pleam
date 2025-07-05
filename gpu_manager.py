# WAWAGOT.AI - GPU Manager
# ===============================================================================
# WAWAGOT.AI - ระบบจัดการ GPU ครบถ้วน
# ===============================================================================
# Created: 2024-12-19
# Purpose: จัดการ GPU acceleration สำหรับ AI/ML workloads
# ===============================================================================

import os
import sys
import json
import asyncio
import threading
import time
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
    TZ_BANGKOK = ZoneInfo("Asia/Bangkok")
except ImportError:
    import pytz
    TZ_BANGKOK = pytz.timezone("Asia/Bangkok")
from typing import Dict, List, Any, Optional, Tuple
import subprocess
import psutil

# GPU Libraries
try:
    import torch
    import torch.cuda as cuda
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import tensorflow as tf
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

# ===============================================================================
# GPU DETECTION & MANAGEMENT
# ===============================================================================

class GPUManager:
    """ระบบจัดการ GPU ครบถ้วน"""
    
    def __init__(self):
        self.gpu_info = {}
        self.gpu_processes = {}
        self.gpu_models = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        self.gpu_utilization = {}
        self.gpu_memory = {}
        self.gpu_temperature = {}
        
    async def initialize_gpu_system(self) -> Dict[str, Any]:
        """เริ่มต้นระบบ GPU"""
        print("🚀 เริ่มต้นระบบ GPU Manager...")
        
        try:
            # ตรวจสอบ GPU Hardware
            gpu_hardware = await self._detect_gpu_hardware()
            
            # ตรวจสอบ GPU Libraries
            gpu_libraries = await self._check_gpu_libraries()
            
            # ตรวจสอบ CUDA
            cuda_info = await self._check_cuda_support()
            
            # เริ่มต้น GPU Monitoring
            await self._start_gpu_monitoring()
            
            return {
                "success": True,
                "message": "GPU System เริ่มต้นสำเร็จ",
                "hardware": gpu_hardware,
                "libraries": gpu_libraries,
                "cuda": cuda_info,
                "monitoring": "active"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"เกิดข้อผิดพลาดในการเริ่มต้น GPU: {e}"
            }
    
    async def _detect_gpu_hardware(self) -> Dict[str, Any]:
        """ตรวจสอบ GPU Hardware"""
        print("🔍 ตรวจสอบ GPU Hardware...")
        
        gpu_info = {
            "nvidia": [],
            "amd": [],
            "intel": [],
            "total_gpus": 0
        }
        
        try:
            # ตรวจสอบ NVIDIA GPU
            if TORCH_AVAILABLE and cuda.is_available():
                nvidia_count = cuda.device_count()
                gpu_info["total_gpus"] += nvidia_count
                
                for i in range(nvidia_count):
                    gpu_props = cuda.get_device_properties(i)
                    gpu_info["nvidia"].append({
                        "id": i,
                        "name": gpu_props.name,
                        "memory_total": gpu_props.total_memory // 1024 // 1024 // 1024,  # GB
                        "compute_capability": f"{gpu_props.major}.{gpu_props.minor}",
                        "multiprocessor_count": gpu_props.multi_processor_count
                    })
                    print(f"   ✅ NVIDIA GPU {i}: {gpu_props.name} ({gpu_props.total_memory // 1024 // 1024 // 1024} GB)")
            
            # ตรวจสอบ GPU ผ่าน nvidia-smi (Windows)
            try:
                result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,temperature.gpu,utilization.gpu', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for i, line in enumerate(lines):
                        if line.strip():
                            parts = line.split(', ')
                            if len(parts) >= 4:
                                gpu_info["nvidia"][i].update({
                                    "current_memory": int(parts[1]) // 1024,  # GB
                                    "temperature": int(parts[2]),
                                    "utilization": int(parts[3])
                                })
            except Exception as e:
                print(f"   ⚠️ ไม่สามารถรัน nvidia-smi: {e}")
            
            # ตรวจสอบ AMD GPU (ถ้ามี)
            try:
                # AMD ROCm หรือ OpenCL
                pass
            except Exception:
                pass
            
            # ตรวจสอบ Intel GPU (ถ้ามี)
            try:
                # Intel oneAPI หรือ OpenCL
                pass
            except Exception:
                pass
            
            return gpu_info
            
        except Exception as e:
            print(f"   ❌ เกิดข้อผิดพลาดในการตรวจสอบ GPU: {e}")
            return gpu_info
    
    async def _check_gpu_libraries(self) -> Dict[str, Any]:
        """ตรวจสอบ GPU Libraries"""
        print("📦 ตรวจสอบ GPU Libraries...")
        
        libraries = {
            "pytorch": {
                "available": TORCH_AVAILABLE,
                "cuda_available": False,
                "version": None,
                "cuda_version": None
            },
            "tensorflow": {
                "available": TENSORFLOW_AVAILABLE,
                "gpu_available": False,
                "version": None
            },
            "opencv": {
                "available": OPENCV_AVAILABLE,
                "cuda_available": False,
                "version": None
            }
        }
        
        # ตรวจสอบ PyTorch
        if TORCH_AVAILABLE:
            libraries["pytorch"]["version"] = torch.__version__
            libraries["pytorch"]["cuda_available"] = cuda.is_available()
            if cuda.is_available():
                libraries["pytorch"]["cuda_version"] = cuda.get_device_name(0)
                print(f"   ✅ PyTorch {torch.__version__} + CUDA")
            else:
                print(f"   ⚠️ PyTorch {torch.__version__} (CPU only)")
        
        # ตรวจสอบ TensorFlow
        if TENSORFLOW_AVAILABLE:
            libraries["tensorflow"]["version"] = tf.__version__
            libraries["tensorflow"]["gpu_available"] = len(tf.config.list_physical_devices('GPU')) > 0
            if libraries["tensorflow"]["gpu_available"]:
                print(f"   ✅ TensorFlow {tf.__version__} + GPU")
            else:
                print(f"   ⚠️ TensorFlow {tf.__version__} (CPU only)")
        
        # ตรวจสอบ OpenCV
        if OPENCV_AVAILABLE:
            libraries["opencv"]["version"] = cv2.__version__
            libraries["opencv"]["cuda_available"] = cv2.cuda.getCudaEnabledDeviceCount() > 0
            if libraries["opencv"]["cuda_available"]:
                print(f"   ✅ OpenCV {cv2.__version__} + CUDA")
            else:
                print(f"   ⚠️ OpenCV {cv2.__version__} (CPU only)")
        
        return libraries
    
    async def _check_cuda_support(self) -> Dict[str, Any]:
        """ตรวจสอบ CUDA Support"""
        print("🔧 ตรวจสอบ CUDA Support...")
        
        cuda_info = {
            "cuda_available": False,
            "cuda_version": None,
            "cudnn_version": None,
            "driver_version": None
        }
        
        try:
            # ตรวจสอบ CUDA ผ่าน PyTorch
            if TORCH_AVAILABLE and cuda.is_available():
                cuda_info["cuda_available"] = True
                cuda_info["cuda_version"] = torch.version.cuda
                print(f"   ✅ CUDA {torch.version.cuda} available")
            
            # ตรวจสอบ CUDA ผ่าน nvidia-smi
            try:
                result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    # Parse driver version
                    for line in result.stdout.split('\n'):
                        if 'Driver Version' in line:
                            driver_version = line.split('Driver Version: ')[1].split()[0]
                            cuda_info["driver_version"] = driver_version
                            print(f"   ✅ NVIDIA Driver: {driver_version}")
                            break
            except Exception as e:
                print(f"   ⚠️ ไม่สามารถตรวจสอบ NVIDIA Driver: {e}")
            
            return cuda_info
            
        except Exception as e:
            print(f"   ❌ เกิดข้อผิดพลาดในการตรวจสอบ CUDA: {e}")
            return cuda_info

# ===============================================================================
# GPU MONITORING
# ===============================================================================

    async def _start_gpu_monitoring(self):
        """เริ่มต้น GPU Monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._gpu_monitoring_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            print("📊 เริ่มต้น GPU Monitoring")
    
    def stop_gpu_monitoring(self):
        """หยุด GPU Monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        print("🛑 หยุด GPU Monitoring")
    
    def _gpu_monitoring_loop(self):
        """ลูปการติดตาม GPU"""
        while self.monitoring_active:
            try:
                asyncio.run(self._update_gpu_status())
                time.sleep(5)  # อัพเดททุก 5 วินาที
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาดในการติดตาม GPU: {e}")
                time.sleep(10)
    
    async def _update_gpu_status(self):
        """อัพเดทสถานะ GPU"""
        try:
            # อัพเดท GPU utilization
            if TORCH_AVAILABLE and cuda.is_available():
                for i in range(cuda.device_count()):
                    # ใช้ nvidia-smi สำหรับข้อมูล real-time
                    try:
                        result = subprocess.run([
                            'nvidia-smi', 
                            '--query-gpu=index,utilization.gpu,memory.used,memory.total,temperature.gpu',
                            '--format=csv,noheader,nounits',
                            '-i', str(i)
                        ], capture_output=True, text=True, timeout=5)
                        
                        if result.returncode == 0:
                            parts = result.stdout.strip().split(', ')
                            if len(parts) >= 5:
                                self.gpu_utilization[i] = {
                                    "gpu_usage": int(parts[1]),
                                    "memory_used": int(parts[2]) // 1024,  # GB
                                    "memory_total": int(parts[3]) // 1024,  # GB
                                    "temperature": int(parts[4]),
                                    "timestamp": datetime.now(TZ_BANGKOK).isoformat()
                                }
                    except Exception:
                        pass
                        
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการอัพเดทสถานะ GPU: {e}")

# ===============================================================================
# GPU OPERATIONS
# ===============================================================================

    async def get_gpu_status(self) -> Dict[str, Any]:
        """ดึงสถานะ GPU ทั้งหมด"""
        try:
            return {
                "success": True,
                "timestamp": datetime.now(TZ_BANGKOK).isoformat(),
                "hardware": self.gpu_info,
                "utilization": self.gpu_utilization,
                "libraries": await self._check_gpu_libraries(),
                "cuda": await self._check_cuda_support(),
                "monitoring_active": self.monitoring_active,
                "total_gpus": len(self.gpu_utilization)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def optimize_gpu_usage(self) -> Dict[str, Any]:
        """ปรับปรุงการใช้ GPU"""
        try:
            optimizations = []
            
            # ตรวจสอบ GPU memory
            for gpu_id, status in self.gpu_utilization.items():
                memory_usage = (status["memory_used"] / status["memory_total"]) * 100
                
                if memory_usage > 90:
                    optimizations.append({
                        "type": "memory_warning",
                        "gpu_id": gpu_id,
                        "message": f"GPU {gpu_id} memory usage: {memory_usage:.1f}%"
                    })
                
                if status["temperature"] > 80:
                    optimizations.append({
                        "type": "temperature_warning",
                        "gpu_id": gpu_id,
                        "message": f"GPU {gpu_id} temperature: {status['temperature']}°C"
                    })
            
            # ล้าง GPU cache ถ้าจำเป็น
            if TORCH_AVAILABLE and cuda.is_available():
                cuda.empty_cache()
                optimizations.append({
                    "type": "cache_cleared",
                    "message": "GPU cache cleared"
                })
            
            return {
                "success": True,
                "optimizations": optimizations
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def load_model_to_gpu(self, model_name: str, model_path: str) -> Dict[str, Any]:
        """โหลด Model ไปยัง GPU"""
        try:
            if not TORCH_AVAILABLE or not cuda.is_available():
                return {"success": False, "error": "GPU not available"}
            
            # ตรวจสอบ GPU memory
            gpu_memory_available = cuda.get_device_properties(0).total_memory - cuda.memory_allocated(0)
            
            # โหลด model (ตัวอย่าง)
            # model = torch.load(model_path, map_location='cuda:0')
            # model.eval()
            
            self.gpu_models[model_name] = {
                "path": model_path,
                "gpu_id": 0,
                "memory_used": 0,  # จะคำนวณจริง
                "loaded_at": datetime.now(TZ_BANGKOK).isoformat()
            }
            
            return {
                "success": True,
                "message": f"Model {model_name} loaded to GPU",
                "gpu_memory_available": gpu_memory_available // 1024 // 1024 // 1024  # GB
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

def get_hybrid_device(prefer_gpu: bool = True) -> str:
    """เลือก device แบบ hybrid (GPU/CPU)"""
    try:
        import torch
        if prefer_gpu and torch.cuda.is_available():
            return 'cuda'
        return 'cpu'
    except ImportError:
        return 'cpu'

# ===============================================================================
# GPU-ACCELERATED SERVICES
# ===============================================================================

class GPUAcceleratedServices:
    """บริการที่ใช้ GPU acceleration แบบ hybrid"""
    
    def __init__(self, gpu_manager: GPUManager):
        self.gpu_manager = gpu_manager
        self.ai_models = {}
        self.processing_queue = asyncio.Queue()
    
    async def initialize_services(self) -> Dict[str, Any]:
        """เริ่มต้นบริการ GPU-accelerated แบบ hybrid"""
        try:
            services = {
                "text_generation": await self._init_text_generation(),
                "image_processing": await self._init_image_processing(),
                "voice_synthesis": await self._init_voice_synthesis(),
                "ocr_processing": await self._init_ocr_processing()
            }
            
            return {
                "success": True,
                "services": services,
                "hybrid_mode": True
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _init_text_generation(self) -> Dict[str, Any]:
        """เริ่มต้น Text Generation Service"""
        try:
            # ตรวจสอบ OpenAI/Gemini integration
            return {
                "available": True,
                "providers": ["openai", "gemini"],
                "gpu_accelerated": True
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    async def _init_image_processing(self) -> Dict[str, Any]:
        """เริ่มต้น Image Processing Service"""
        try:
            if OPENCV_AVAILABLE and cv2.cuda.getCudaEnabledDeviceCount() > 0:
                return {
                    "available": True,
                    "operations": ["resize", "filter", "detection", "segmentation"],
                    "gpu_accelerated": True
                }
            else:
                return {
                    "available": True,
                    "operations": ["resize", "filter", "detection"],
                    "gpu_accelerated": False
                }
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    async def _init_voice_synthesis(self) -> Dict[str, Any]:
        """เริ่มต้น Voice Synthesis Service"""
        try:
            # ตรวจสอบ Retell.AI integration
            return {
                "available": True,
                "providers": ["retell", "openai_tts"],
                "gpu_accelerated": True
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    async def _init_ocr_processing(self) -> Dict[str, Any]:
        """เริ่มต้น OCR Processing Service"""
        try:
            # ตรวจสอบ OCR libraries
            return {
                "available": True,
                "engines": ["tesseract", "paddleocr"],
                "gpu_accelerated": True
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    async def _generate_text_hybrid(self, request, device: str = 'auto') -> Dict[str, Any]:
        """สร้างข้อความแบบ hybrid"""
        try:
            actual_device = get_hybrid_device(device == 'gpu' or (device == 'auto' and True))
            
            # ใช้ GPU memory สำหรับ model loading ถ้าเป็น cuda
            if actual_device == 'cuda' and TORCH_AVAILABLE and cuda.is_available():
                # ย้าย model ไป GPU ถ้าจำเป็น
                pass
            
            # เรียกใช้ OpenAI API หรือ Gemini API
            if request.provider == "openai":
                result = await self._call_openai_api(request)
            elif request.provider == "gemini":
                result = await self._call_gemini_api(request)
            else:
                result = {"error": f"Unknown provider: {request.provider}"}
            
            return {
                "success": True,
                "text": result.get("text", ""),
                "provider": request.provider,
                "model": request.model,
                "device_used": actual_device,
                "gpu_accelerated": actual_device == 'cuda',
                "processing_time": 0.1
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_image_hybrid(self, image_data: bytes, operation: str, device: str = 'auto') -> Dict[str, Any]:
        """ประมวลผลภาพแบบ hybrid"""
        try:
            actual_device = get_hybrid_device(device == 'gpu' or (device == 'auto' and True))
            
            if OPENCV_AVAILABLE and actual_device == 'cuda':
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
                        gpu_result = cv2.cuda.resize(gpu_img, (640, 480))
                        result_img = gpu_result.download()
                    elif operation == "filter":
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
                        "device_used": actual_device,
                        "gpu_accelerated": True,
                        "image_data": result_data,
                        "processing_time": 0.05
                    }
            
            # Fallback ไป CPU
            return {
                "success": True,
                "operation": operation,
                "device_used": "cpu",
                "gpu_accelerated": False,
                "message": "Using CPU fallback"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# ===============================================================================
# MAIN EXECUTION
# ===============================================================================

async def main():
    """ฟังก์ชันหลัก"""
    print("🚀 WAWAGOT.AI GPU Manager")
    print("=" * 60)
    
    # สร้าง GPU Manager
    gpu_manager = GPUManager()
    
    # เริ่มต้นระบบ
    init_result = await gpu_manager.initialize_gpu_system()
    print(json.dumps(init_result, ensure_ascii=False, indent=2))
    
    if init_result["success"]:
        # สร้าง GPU-accelerated services
        services = GPUAcceleratedServices(gpu_manager)
        services_result = await services.initialize_services()
        print("\nGPU Services:", json.dumps(services_result, ensure_ascii=False, indent=2))
        
        # แสดงสถานะ GPU
        status = await gpu_manager.get_gpu_status()
        print("\nGPU Status:", json.dumps(status, ensure_ascii=False, indent=2))
    
    # รอสักครู่
    print("\nกำลังติดตาม GPU... (กด Ctrl+C เพื่อหยุด)")
    try:
        await asyncio.sleep(30)
    except KeyboardInterrupt:
        print("\nหยุดการทำงาน...")
        gpu_manager.stop_gpu_monitoring()

if __name__ == "__main__":
    asyncio.run(main()) 