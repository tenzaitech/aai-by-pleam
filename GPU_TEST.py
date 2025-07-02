#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPU Test Script for TensorFlow
"""

import sys
import os

def test_tensorflow_gpu():
    """ทดสอบ TensorFlow GPU Support"""
    try:
        print("🔍 กำลังทดสอบ TensorFlow GPU Support...")
        
        import tensorflow as tf
        print(f"✅ TensorFlow Version: {tf.version.VERSION}")
        
        # ตรวจสอบ GPU Devices
        gpu_devices = tf.config.list_physical_devices('GPU')
        cpu_devices = tf.config.list_physical_devices('CPU')
        
        print(f"🖥️  CPU Devices: {len(cpu_devices)}")
        print(f"🎮 GPU Devices: {len(gpu_devices)}")
        
        if gpu_devices:
            print("✅ GPU พบและพร้อมใช้งาน!")
            for i, gpu in enumerate(gpu_devices):
                print(f"   GPU {i}: {gpu.name}")
            
            # ทดสอบ GPU Memory
            try:
                with tf.device('/GPU:0'):
                    a = tf.constant([[1.0, 2.0], [3.0, 4.0]])
                    b = tf.constant([[1.0, 1.0], [0.0, 1.0]])
                    c = tf.matmul(a, b)
                    print(f"✅ GPU Matrix Test: {c.numpy()}")
            except Exception as e:
                print(f"⚠️  GPU Matrix Test Failed: {e}")
        else:
            print("⚠️  ไม่พบ GPU หรือ TensorFlow ไม่สามารถเข้าถึง GPU ได้")
            print("💡 ข้อเสนอแนะ:")
            print("   1. ตรวจสอบ NVIDIA Driver")
            print("   2. ตรวจสอบ CUDA Installation")
            print("   3. ตรวจสอบ cuDNN Installation")
            print("   4. ตรวจสอบ Environment Variables")
        
        return True
        
    except ImportError as e:
        print(f"❌ ไม่สามารถ import TensorFlow: {e}")
        return False
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        return False

def test_cuda_environment():
    """ทดสอบ CUDA Environment"""
    print("\n🔍 กำลังตรวจสอบ CUDA Environment...")
    
    # ตรวจสอบ Environment Variables
    cuda_path = os.environ.get('CUDA_PATH')
    cuda_home = os.environ.get('CUDA_HOME')
    
    print(f"CUDA_PATH: {cuda_path}")
    print(f"CUDA_HOME: {cuda_home}")
    
    # ตรวจสอบ PATH
    path_entries = os.environ.get('PATH', '').split(';')
    cuda_paths = [p for p in path_entries if 'cuda' in p.lower()]
    
    if cuda_paths:
        print("✅ พบ CUDA ใน PATH:")
        for path in cuda_paths:
            print(f"   {path}")
    else:
        print("⚠️  ไม่พบ CUDA ใน PATH")

def main():
    """Main function"""
    print("🚀 เริ่มทดสอบ GPU Support")
    print("=" * 50)
    
    # ทดสอบ CUDA Environment
    test_cuda_environment()
    
    # ทดสอบ TensorFlow GPU
    success = test_tensorflow_gpu()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ การทดสอบเสร็จสิ้น")
    else:
        print("❌ การทดสอบล้มเหลว")
    
    print("\nกด Enter เพื่อปิด...")
    input()

if __name__ == "__main__":
    main() 