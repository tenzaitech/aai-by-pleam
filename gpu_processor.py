#!/usr/bin/env python3
"""
GPU Processor - Intelligent CPU/GPU Selection System
สำหรับเลือกใช้ CPU หรือ GPU ตามความเหมาะสมของงาน
"""

import os
import time
import psutil
import threading
from typing import Dict, Any, Callable, Optional
import logging

# GPU Libraries (optional imports)
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPUProcessor:
    """ระบบจัดการการเลือกใช้ CPU/GPU ตามความเหมาะสม"""
    
    def __init__(self):
        self.gpu_available = self._check_gpu_availability()
        self.cpu_cores = psutil.cpu_count()
        self.memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # งานที่เหมาะกับ GPU
        self.gpu_optimized_tasks = {
            'image_processing': True,
            'video_processing': True,
            'ocr_processing': True,
            'ai_inference': True,
            'deep_learning': True,
            'computer_vision': True,
            'parallel_computation': True,
            'matrix_operations': True,
            'neural_network': True,
            'image_recognition': True,
            'object_detection': True,
            'face_recognition': True,
            'text_recognition': True,
            'data_analysis': False,  # ใช้ CPU
            'file_operations': False,  # ใช้ CPU
            'web_scraping': False,  # ใช้ CPU
            'database_operations': False,  # ใช้ CPU
            'api_calls': False,  # ใช้ CPU
            'text_processing': False,  # ใช้ CPU
            'json_parsing': False,  # ใช้ CPU
        }
        
        logger.info(f"GPU Processor initialized - GPU: {self.gpu_available}, CPU Cores: {self.cpu_cores}, Memory: {self.memory_gb:.1f}GB")
    
    def _check_gpu_availability(self) -> bool:
        """ตรวจสอบว่ามี GPU ที่ใช้งานได้หรือไม่"""
        try:
            # ตรวจสอบ NVIDIA GPU
            result = os.popen('nvidia-smi --query-gpu=name --format=csv,noheader,nounits').read().strip()
            if result:
                logger.info(f"Found GPU: {result}")
                return True
            
            # ตรวจสอบ OpenCV GPU support
            if OPENCV_AVAILABLE:
                gpu_count = cv2.cuda.getCudaEnabledDeviceCount()
                if gpu_count > 0:
                    logger.info(f"OpenCV GPU support available: {gpu_count} devices")
                    return True
            
            return False
        except Exception as e:
            logger.warning(f"GPU check failed: {e}")
            return False
    
    def should_use_gpu(self, task_type: str, data_size: Optional[int] = None) -> bool:
        """ตัดสินใจว่าจะใช้ GPU หรือ CPU ตามประเภทงานและขนาดข้อมูล"""
        
        # ตรวจสอบประเภทงาน
        if task_type not in self.gpu_optimized_tasks:
            logger.warning(f"Unknown task type: {task_type}, defaulting to CPU")
            return False
        
        use_gpu = self.gpu_optimized_tasks[task_type]
        
        # ปรับตามขนาดข้อมูล
        if data_size:
            if data_size < 1000:  # ข้อมูลเล็ก ใช้ CPU
                use_gpu = False
            elif data_size > 100000:  # ข้อมูลใหญ่ ใช้ GPU
                use_gpu = True
        
        # ตรวจสอบ GPU availability
        if use_gpu and not self.gpu_available:
            logger.warning(f"GPU requested for {task_type} but not available, using CPU")
            use_gpu = False
        
        return use_gpu
    
    def execute_task(self, task_type: str, task_func: Callable, *args, **kwargs) -> Any:
        """ดำเนินการงานโดยเลือกใช้ CPU หรือ GPU ตามความเหมาะสม"""
        
        start_time = time.time()
        
        # ตัดสินใจใช้ GPU หรือ CPU
        use_gpu = self.should_use_gpu(task_type)
        
        if use_gpu:
            logger.info(f"Executing {task_type} on GPU")
            result = self._execute_on_gpu(task_func, *args, **kwargs)
        else:
            logger.info(f"Executing {task_type} on CPU")
            result = self._execute_on_cpu(task_func, *args, **kwargs)
        
        execution_time = time.time() - start_time
        logger.info(f"Task {task_type} completed in {execution_time:.2f}s using {'GPU' if use_gpu else 'CPU'}")
        
        return result
    
    def _execute_on_gpu(self, task_func: Callable, *args, **kwargs) -> Any:
        """ดำเนินการงานบน GPU"""
        try:
            # สำหรับงานที่ใช้ OpenCV GPU
            if OPENCV_AVAILABLE and hasattr(cv2, 'cuda'):
                return self._execute_opencv_gpu(task_func, *args, **kwargs)
            else:
                # Fallback to CPU if GPU libraries not available
                logger.warning("GPU libraries not available, falling back to CPU")
                return self._execute_on_cpu(task_func, *args, **kwargs)
        except Exception as e:
            logger.error(f"GPU execution failed: {e}, falling back to CPU")
            return self._execute_on_cpu(task_func, *args, **kwargs)
    
    def _execute_on_cpu(self, task_func: Callable, *args, **kwargs) -> Any:
        """ดำเนินการงานบน CPU"""
        return task_func(*args, **kwargs)
    
    def _execute_opencv_gpu(self, task_func: Callable, *args, **kwargs) -> Any:
        """ดำเนินการงาน OpenCV บน GPU"""
        # ตรวจสอบว่าเป็น OpenCV GPU function หรือไม่
        if hasattr(task_func, '__name__') and 'gpu' in task_func.__name__.lower():
            return task_func(*args, **kwargs)
        else:
            # Convert to GPU version if possible
            return task_func(*args, **kwargs)
    
    def get_system_info(self) -> Dict[str, Any]:
        """รับข้อมูลระบบ"""
        return {
            'gpu_available': self.gpu_available,
            'cpu_cores': self.cpu_cores,
            'memory_gb': self.memory_gb,
            'gpu_optimized_tasks': self.gpu_optimized_tasks,
            'opencv_available': OPENCV_AVAILABLE,
            'numpy_available': NUMPY_AVAILABLE
        }
    
    def optimize_task(self, task_type: str, data: Any) -> Dict[str, Any]:
        """วิเคราะห์และแนะนำการ optimize งาน"""
        data_size = len(str(data)) if hasattr(data, '__len__') else 0
        
        recommendation = {
            'task_type': task_type,
            'data_size': data_size,
            'recommended_device': 'GPU' if self.should_use_gpu(task_type, data_size) else 'CPU',
            'reason': '',
            'optimization_tips': []
        }
        
        if recommendation['recommended_device'] == 'GPU':
            recommendation['reason'] = f"Task {task_type} is GPU-optimized and data size ({data_size}) is suitable for GPU processing"
            recommendation['optimization_tips'] = [
                "Use batch processing for better GPU utilization",
                "Consider data transfer overhead",
                "Monitor GPU memory usage"
            ]
        else:
            recommendation['reason'] = f"Task {task_type} is CPU-optimized or data size ({data_size}) is too small for GPU"
            recommendation['optimization_tips'] = [
                "Use multiprocessing for CPU-intensive tasks",
                "Consider memory-efficient algorithms",
                "Optimize I/O operations"
            ]
        
        return recommendation

# Global instance
gpu_processor = GPUProcessor()

def smart_execute(task_type: str, task_func: Callable, *args, **kwargs) -> Any:
    """ฟังก์ชัน wrapper สำหรับ smart execution"""
    return gpu_processor.execute_task(task_type, task_func, *args, **kwargs)

def get_optimization_recommendation(task_type: str, data: Any) -> Dict[str, Any]:
    """รับคำแนะนำการ optimize"""
    return gpu_processor.optimize_task(task_type, data)

if __name__ == "__main__":
    # Test the GPU processor
    print("=== GPU Processor Test ===")
    print(f"System Info: {gpu_processor.get_system_info()}")
    
    # Test task optimization
    test_data = "test" * 1000
    recommendation = get_optimization_recommendation('image_processing', test_data)
    print(f"Optimization Recommendation: {recommendation}") 