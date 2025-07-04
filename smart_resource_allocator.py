#!/usr/bin/env python3
"""
AI Smart Resource Allocator - WAWA
พิจารณาใช้ GPU/CPU ตามความเหมาะสม
"""

import torch
import numpy as np
import psutil
import time
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
from typing import Dict, Any, Callable
import queue

class SmartResourceAllocator:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.cpu_cores = multiprocessing.cpu_count()
        self.gpu_memory = torch.cuda.get_device_properties(0).total_memory if torch.cuda.is_available() else 0
        self.task_queue = queue.Queue()
        self.results = {}
        
    def analyze_task(self, task_type: str, data_size: int, complexity: str) -> Dict[str, Any]:
        """AI วิเคราะห์งานและเลือก resource ที่เหมาะสม"""
        
        # ตรวจสอบ system resources
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        gpu_memory_used = torch.cuda.memory_allocated(0) if torch.cuda.is_available() else 0
        
        # AI Decision Matrix
        decision = {
            'task_type': task_type,
            'data_size': data_size,
            'complexity': complexity,
            'recommended_device': 'cpu',
            'reason': '',
            'estimated_time': 0,
            'resource_usage': {}
        }
        
        # วิเคราะห์ตามประเภทงาน
        if task_type in ['matrix_multiplication', 'neural_network', 'image_processing', 'large_data_processing']:
            if torch.cuda.is_available() and data_size > 10000:
                decision['recommended_device'] = 'gpu'
                decision['reason'] = 'Large data + GPU-optimized task'
            else:
                decision['recommended_device'] = 'cpu'
                decision['reason'] = 'Small data or CPU-optimized task'
        
        elif task_type in ['file_io', 'network_request', 'string_processing', 'logic_operations']:
            decision['recommended_device'] = 'cpu'
            decision['reason'] = 'I/O bound or logic operations'
        
        elif task_type in ['parallel_computation', 'batch_processing']:
            if cpu_percent < 70 and self.cpu_cores > 4:
                decision['recommended_device'] = 'cpu_parallel'
                decision['reason'] = 'Multi-core CPU available'
            elif torch.cuda.is_available():
                decision['recommended_device'] = 'gpu'
                decision['reason'] = 'GPU parallel processing'
            else:
                decision['recommended_device'] = 'cpu'
                decision['reason'] = 'Single CPU processing'
        
        # ประมาณเวลาที่ใช้
        if decision['recommended_device'] == 'gpu':
            decision['estimated_time'] = data_size * 0.0001  # GPU เร็ว
        elif decision['recommended_device'] == 'cpu_parallel':
            decision['estimated_time'] = data_size * 0.001 / self.cpu_cores  # Parallel CPU
        else:
            decision['estimated_time'] = data_size * 0.001  # Single CPU
        
        # Resource usage estimation
        decision['resource_usage'] = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'gpu_memory_used': gpu_memory_used / 1024**2 if gpu_memory_used > 0 else 0
        }
        
        return decision
    
    def execute_on_gpu(self, task_func: Callable, *args, **kwargs):
        """ทำงานบน GPU"""
        try:
            start_time = time.time()
            result = task_func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            return {
                'result': result,
                'device': 'gpu',
                'execution_time': execution_time,
                'success': True
            }
        except Exception as e:
            return {
                'result': None,
                'device': 'gpu',
                'error': str(e),
                'success': False
            }
    
    def execute_on_cpu(self, task_func: Callable, *args, **kwargs):
        """ทำงานบน CPU"""
        try:
            start_time = time.time()
            result = task_func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            return {
                'result': result,
                'device': 'cpu',
                'execution_time': execution_time,
                'success': True
            }
        except Exception as e:
            return {
                'result': None,
                'device': 'cpu',
                'error': str(e),
                'success': False
            }
    
    def execute_on_cpu_parallel(self, task_func: Callable, data, num_workers=None):
        """ทำงานบน CPU แบบ parallel"""
        if num_workers is None:
            num_workers = min(self.cpu_cores, 8)
        
        try:
            start_time = time.time()
            
            # แบ่งข้อมูลเป็น chunks
            chunk_size = len(data) // num_workers
            chunks = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
            
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = [executor.submit(task_func, chunk) for chunk in chunks]
                results = [future.result() for future in futures]
            
            execution_time = time.time() - start_time
            
            return {
                'result': results,
                'device': 'cpu_parallel',
                'execution_time': execution_time,
                'workers_used': num_workers,
                'success': True
            }
        except Exception as e:
            return {
                'result': None,
                'device': 'cpu_parallel',
                'error': str(e),
                'success': False
            }
    
    def smart_execute(self, task_func: Callable, task_type: str, data_size: int, complexity: str, *args, **kwargs):
        """AI ทำงานแบบ smart"""
        
        # วิเคราะห์งาน
        analysis = self.analyze_task(task_type, data_size, complexity)
        
        print(f"🧠 AI Analysis:")
        print(f"   Task: {task_type}")
        print(f"   Data Size: {data_size}")
        print(f"   Recommended: {analysis['recommended_device']}")
        print(f"   Reason: {analysis['reason']}")
        print(f"   Estimated Time: {analysis['estimated_time']:.3f}s")
        
        # ทำงานตามที่ AI แนะนำ
        if analysis['recommended_device'] == 'gpu':
            print(f"🚀 Executing on GPU...")
            result = self.execute_on_gpu(task_func, *args, **kwargs)
        elif analysis['recommended_device'] == 'cpu_parallel':
            print(f"⚡ Executing on CPU (Parallel)...")
            result = self.execute_on_cpu_parallel(task_func, *args, **kwargs)
        else:
            print(f"💻 Executing on CPU...")
            result = self.execute_on_cpu(task_func, *args, **kwargs)
        
        # แสดงผลลัพธ์
        if result['success']:
            print(f"✅ Success! Device: {result['device']}, Time: {result['execution_time']:.3f}s")
        else:
            print(f"❌ Failed! Error: {result.get('error', 'Unknown')}")
        
        return result

# ตัวอย่าง Task Functions
def matrix_multiplication_task(data):
    """Matrix multiplication task"""
    if isinstance(data, torch.Tensor):
        return torch.mm(data, data.T)
    else:
        return np.dot(data, data.T)

def neural_network_task(data):
    """Neural network task"""
    if torch.cuda.is_available():
        data = torch.tensor(data, device='cuda', dtype=torch.float32)
    else:
        data = torch.tensor(data, dtype=torch.float32)
    
    # Simple neural network
    model = torch.nn.Sequential(
        torch.nn.Linear(data.shape[1], 64),
        torch.nn.ReLU(),
        torch.nn.Linear(64, 32),
        torch.nn.ReLU(),
        torch.nn.Linear(32, 1)
    )
    
    if torch.cuda.is_available():
        model = model.cuda()
    
    output = model(data)
    return output.mean().item()

def file_processing_task(data):
    """File processing task (CPU-bound)"""
    result = 0
    for item in data:
        result += sum(item) if hasattr(item, '__iter__') else item
    return result

def parallel_computation_task(data):
    """Parallel computation task"""
    return [x * 2 + 1 for x in data]

# Test Functions
def test_smart_allocator():
    """ทดสอบ Smart Resource Allocator"""
    allocator = SmartResourceAllocator()
    
    print("🧠 AI Smart Resource Allocator - WAWA")
    print("=" * 50)
    
    # Test 1: Matrix Multiplication (GPU)
    print("\n1. Matrix Multiplication (Large Data)")
    large_matrix = torch.randn(5000, 5000)
    result1 = allocator.smart_execute(
        matrix_multiplication_task, 
        'matrix_multiplication', 
        5000*5000, 
        'high',
        large_matrix
    )
    
    # Test 2: Neural Network (GPU)
    print("\n2. Neural Network Processing")
    nn_data = torch.randn(1000, 100)
    result2 = allocator.smart_execute(
        neural_network_task,
        'neural_network',
        1000*100,
        'high',
        nn_data
    )
    
    # Test 3: File Processing (CPU)
    print("\n3. File Processing")
    file_data = list(range(100000))
    result3 = allocator.smart_execute(
        file_processing_task,
        'file_io',
        100000,
        'medium',
        file_data
    )
    
    # Test 4: Parallel Computation (CPU Parallel)
    print("\n4. Parallel Computation")
    parallel_data = list(range(1000000))
    result4 = allocator.smart_execute(
        parallel_computation_task,
        'parallel_computation',
        1000000,
        'medium',
        parallel_data
    )
    
    print("\n🎯 All tests completed!")

if __name__ == "__main__":
    test_smart_allocator() 