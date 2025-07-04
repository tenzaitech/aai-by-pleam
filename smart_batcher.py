"""
Smart Batch Processor
ประมวลผลหลายงานพร้อมกันอย่างมีประสิทธิภาพ
"""

import asyncio
from typing import List, Callable, Any, Dict
import time
from dataclasses import dataclass

@dataclass
class BatchJob:
    name: str
    func: Callable
    args: tuple = ()
    priority: int = 1

class SmartBatcher:
    def __init__(self, max_concurrent: int = 4):
        self.max_concurrent = max_concurrent
        self.jobs: List[BatchJob] = []
        self.results = {}
        
    def add_job(self, job: BatchJob):
        """เพิ่มงานเข้า batch"""
        self.jobs.append(job)
        
    async def process_batch(self) -> Dict[str, Any]:
        """ประมวลผล batch ทั้งหมด"""
        print(f"🚀 เริ่มประมวลผล {len(self.jobs)} งาน...")
        
        # เรียงลำดับตาม priority
        self.jobs.sort(key=lambda x: x.priority, reverse=True)
        
        # แบ่งงานเป็น chunks
        chunks = [self.jobs[i:i + self.max_concurrent] 
                 for i in range(0, len(self.jobs), self.max_concurrent)]
        
        for i, chunk in enumerate(chunks):
            print(f"📦 ประมวลผล chunk {i+1}/{len(chunks)}")
            
            # รันงานพร้อมกัน
            tasks = []
            for job in chunk:
                task = asyncio.create_task(self._run_job(job))
                tasks.append(task)
            
            # รอให้เสร็จ
            chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # เก็บผลลัพธ์
            for job, result in zip(chunk, chunk_results):
                self.results[job.name] = result
                
        print("✅ ประมวลผลเสร็จสิ้น")
        return self.results
        
    async def _run_job(self, job: BatchJob) -> Any:
        """รันงานเดียว"""
        try:
            start_time = time.time()
            
            if asyncio.iscoroutinefunction(job.func):
                result = await job.func(*job.args)
            else:
                result = job.func(*job.args)
                
            end_time = time.time()
            print(f"✅ {job.name} เสร็จใน {end_time - start_time:.2f} วินาที")
            
            return result
            
        except Exception as e:
            print(f"❌ {job.name} ผิดพลาด: {e}")
            return None

# ตัวอย่างการใช้งาน
async def example_job(name: str, delay: float):
    """ตัวอย่างงาน"""
    await asyncio.sleep(delay)
    return f"เสร็จ {name}"

async def main():
    batcher = SmartBatcher(max_concurrent=3)
    
    # เพิ่มงาน
    batcher.add_job(BatchJob("งาน 1", example_job, ("งาน 1", 1.0), priority=3))
    batcher.add_job(BatchJob("งาน 2", example_job, ("งาน 2", 0.5), priority=2))
    batcher.add_job(BatchJob("งาน 3", example_job, ("งาน 3", 2.0), priority=1))
    batcher.add_job(BatchJob("งาน 4", example_job, ("งาน 4", 0.3), priority=4))
    
    # ประมวลผล
    results = await batcher.process_batch()
    
    print("📊 ผลลัพธ์:", results)

if __name__ == "__main__":
    asyncio.run(main()) 