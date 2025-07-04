#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workflow Monitor - ระบบติดตาม workflow แบบ real-time
ติดตามสถานะและประสิทธิภาพของ workflow ต่างๆ
"""

import time
import threading
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import psutil
import sqlite3

class WorkflowStatus(Enum):
    """สถานะของ workflow"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StepStatus(Enum):
    """สถานะของ workflow step"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowStep:
    """ข้อมูล workflow step"""
    step_id: str
    step_name: str
    module: str
    status: StepStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None
    logs: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.logs is None:
            self.logs = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class WorkflowInfo:
    """ข้อมูล workflow"""
    workflow_id: str
    workflow_type: str
    status: WorkflowStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    total_duration_ms: int = 0
    steps: List[WorkflowStep] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []
        if self.metadata is None:
            self.metadata = {}

class WorkflowMonitor:
    """ระบบติดตาม workflow แบบ real-time"""
    
    def __init__(self, logger_manager=None):
        self.logger_manager = logger_manager
        self.active_workflows: Dict[str, WorkflowInfo] = {}
        self.workflow_history: List[WorkflowInfo] = []
        self.callbacks: Dict[str, List[Callable]] = {
            "workflow_started": [],
            "workflow_completed": [],
            "workflow_failed": [],
            "step_started": [],
            "step_completed": [],
            "step_failed": []
        }
        
        # Thread lock
        self.lock = threading.Lock()
        
        # Performance tracking
        self.performance_metrics = {
            "cpu_usage": [],
            "memory_usage": [],
            "disk_io": [],
            "network_io": []
        }
        
        # เริ่ม background monitoring
        self._start_monitoring()
        
        print("🔍 Workflow Monitor initialized")
    
    def create_workflow(self, workflow_type: str, metadata: Dict[str, Any] = None) -> str:
        """สร้าง workflow ใหม่"""
        workflow_id = str(uuid.uuid4())
        
        workflow = WorkflowInfo(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            status=WorkflowStatus.PENDING,
            start_time=datetime.now(),
            metadata=metadata or {}
        )
        
        with self.lock:
            self.active_workflows[workflow_id] = workflow
        
        # บันทึก log
        if self.logger_manager:
            self.logger_manager.log(
                module="workflow_monitor",
                level="INFO",
                message=f"Created workflow: {workflow_type}",
                workflow_id=workflow_id,
                metadata=metadata
            )
        
        return workflow_id
    
    def start_workflow(self, workflow_id: str) -> bool:
        """เริ่มต้น workflow"""
        with self.lock:
            if workflow_id not in self.active_workflows:
                return False
            
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.RUNNING
            workflow.start_time = datetime.now()
        
        # บันทึก log
        if self.logger_manager:
            self.logger_manager.log(
                module="workflow_monitor",
                level="INFO",
                message=f"Started workflow: {workflow.workflow_type}",
                workflow_id=workflow_id,
                status="running"
            )
        
        # เรียก callbacks
        self._trigger_callbacks("workflow_started", workflow)
        
        return True
    
    def add_step(self, workflow_id: str, step_name: str, module: str, 
                metadata: Dict[str, Any] = None) -> str:
        """เพิ่ม step ใน workflow"""
        step_id = str(uuid.uuid4())
        
        step = WorkflowStep(
            step_id=step_id,
            step_name=step_name,
            module=module,
            status=StepStatus.PENDING,
            start_time=datetime.now(),
            metadata=metadata or {}
        )
        
        with self.lock:
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                workflow.steps.append(step)
                workflow.total_steps = len(workflow.steps)
        
        return step_id
    
    def start_step(self, workflow_id: str, step_id: str) -> bool:
        """เริ่มต้น step"""
        with self.lock:
            if workflow_id not in self.active_workflows:
                return False
            
            workflow = self.active_workflows[workflow_id]
            step = self._find_step(workflow, step_id)
            
            if not step:
                return False
            
            step.status = StepStatus.RUNNING
            step.start_time = datetime.now()
        
        # บันทึก log
        if self.logger_manager:
            self.logger_manager.log(
                module="workflow_monitor",
                level="INFO",
                message=f"Started step: {step.step_name}",
                workflow_id=workflow_id,
                step=step_id,
                status="running"
            )
        
        # เรียก callbacks
        self._trigger_callbacks("step_started", workflow, step)
        
        return True
    
    def complete_step(self, workflow_id: str, step_id: str, 
                     duration_ms: int = None, logs: List[Dict] = None) -> bool:
        """เสร็จสิ้น step"""
        with self.lock:
            if workflow_id not in self.active_workflows:
                return False
            
            workflow = self.active_workflows[workflow_id]
            step = self._find_step(workflow, step_id)
            
            if not step:
                return False
            
            step.status = StepStatus.COMPLETED
            step.end_time = datetime.now()
            step.duration_ms = duration_ms
            if logs:
                step.logs.extend(logs)
            
            workflow.completed_steps += 1
        
        # บันทึก log
        if self.logger_manager:
            self.logger_manager.log(
                module="workflow_monitor",
                level="INFO",
                message=f"Completed step: {step.step_name}",
                workflow_id=workflow_id,
                step=step_id,
                status="completed",
                duration_ms=duration_ms
            )
        
        # เรียก callbacks
        self._trigger_callbacks("step_completed", workflow, step)
        
        return True
    
    def fail_step(self, workflow_id: str, step_id: str, 
                 error_message: str = None, logs: List[Dict] = None) -> bool:
        """ล้มเหลว step"""
        with self.lock:
            if workflow_id not in self.active_workflows:
                return False
            
            workflow = self.active_workflows[workflow_id]
            step = self._find_step(workflow, step_id)
            
            if not step:
                return False
            
            step.status = StepStatus.FAILED
            step.end_time = datetime.now()
            if logs:
                step.logs.extend(logs)
            
            workflow.failed_steps += 1
        
        # บันทึก log
        if self.logger_manager:
            self.logger_manager.log(
                module="workflow_monitor",
                level="ERROR",
                message=f"Failed step: {step.step_name} - {error_message}",
                workflow_id=workflow_id,
                step=step_id,
                status="failed"
            )
        
        # เรียก callbacks
        self._trigger_callbacks("step_failed", workflow, step)
        
        return True
    
    def complete_workflow(self, workflow_id: str) -> bool:
        """เสร็จสิ้น workflow"""
        with self.lock:
            if workflow_id not in self.active_workflows:
                return False
            
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.COMPLETED
            workflow.end_time = datetime.now()
            
            if workflow.end_time and workflow.start_time:
                workflow.total_duration_ms = int(
                    (workflow.end_time - workflow.start_time).total_seconds() * 1000
                )
            
            # ย้ายไปยัง history
            self.workflow_history.append(workflow)
            del self.active_workflows[workflow_id]
        
        # บันทึก log
        if self.logger_manager:
            self.logger_manager.log(
                module="workflow_monitor",
                level="INFO",
                message=f"Completed workflow: {workflow.workflow_type}",
                workflow_id=workflow_id,
                status="completed",
                duration_ms=workflow.total_duration_ms
            )
        
        # เรียก callbacks
        self._trigger_callbacks("workflow_completed", workflow)
        
        return True
    
    def fail_workflow(self, workflow_id: str, error_message: str = None) -> bool:
        """ล้มเหลว workflow"""
        with self.lock:
            if workflow_id not in self.active_workflows:
                return False
            
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.FAILED
            workflow.end_time = datetime.now()
            
            if workflow.end_time and workflow.start_time:
                workflow.total_duration_ms = int(
                    (workflow.end_time - workflow.start_time).total_seconds() * 1000
                )
            
            # ย้ายไปยัง history
            self.workflow_history.append(workflow)
            del self.active_workflows[workflow_id]
        
        # บันทึก log
        if self.logger_manager:
            self.logger_manager.log(
                module="workflow_monitor",
                level="ERROR",
                message=f"Failed workflow: {workflow.workflow_type} - {error_message}",
                workflow_id=workflow_id,
                status="failed"
            )
        
        # เรียก callbacks
        self._trigger_callbacks("workflow_failed", workflow)
        
        return True
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """ดึงสถานะ workflow"""
        with self.lock:
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
            else:
                # ค้นหาใน history
                for workflow in self.workflow_history:
                    if workflow.workflow_id == workflow_id:
                        break
                else:
                    return None
            
            return {
                "workflow_id": workflow.workflow_id,
                "workflow_type": workflow.workflow_type,
                "status": workflow.status.value,
                "start_time": workflow.start_time.isoformat(),
                "end_time": workflow.end_time.isoformat() if workflow.end_time else None,
                "total_steps": workflow.total_steps,
                "completed_steps": workflow.completed_steps,
                "failed_steps": workflow.failed_steps,
                "total_duration_ms": workflow.total_duration_ms,
                "progress_percentage": self._calculate_progress(workflow),
                "steps": [self._step_to_dict(step) for step in workflow.steps],
                "metadata": workflow.metadata
            }
    
    def get_active_workflows(self) -> List[Dict[str, Any]]:
        """ดึง workflows ที่กำลังทำงานอยู่"""
        with self.lock:
            return [
                {
                    "workflow_id": workflow.workflow_id,
                    "workflow_type": workflow.workflow_type,
                    "status": workflow.status.value,
                    "start_time": workflow.start_time.isoformat(),
                    "total_steps": workflow.total_steps,
                    "completed_steps": workflow.completed_steps,
                    "failed_steps": workflow.failed_steps,
                    "progress_percentage": self._calculate_progress(workflow)
                }
                for workflow in self.active_workflows.values()
            ]
    
    def get_workflow_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """ดึงประวัติ workflow"""
        with self.lock:
            recent_history = self.workflow_history[-limit:] if self.workflow_history else []
            return [
                {
                    "workflow_id": workflow.workflow_id,
                    "workflow_type": workflow.workflow_type,
                    "status": workflow.status.value,
                    "start_time": workflow.start_time.isoformat(),
                    "end_time": workflow.end_time.isoformat() if workflow.end_time else None,
                    "total_duration_ms": workflow.total_duration_ms,
                    "total_steps": workflow.total_steps,
                    "completed_steps": workflow.completed_steps,
                    "failed_steps": workflow.failed_steps
                }
                for workflow in recent_history
            ]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """ดึง performance metrics"""
        return {
            "cpu_usage": self.performance_metrics["cpu_usage"][-100:] if self.performance_metrics["cpu_usage"] else [],
            "memory_usage": self.performance_metrics["memory_usage"][-100:] if self.performance_metrics["memory_usage"] else [],
            "disk_io": self.performance_metrics["disk_io"][-100:] if self.performance_metrics["disk_io"] else [],
            "network_io": self.performance_metrics["network_io"][-100:] if self.performance_metrics["network_io"] else []
        }
    
    def add_callback(self, event: str, callback: Callable):
        """เพิ่ม callback สำหรับ event"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def _find_step(self, workflow: WorkflowInfo, step_id: str) -> Optional[WorkflowStep]:
        """ค้นหา step ใน workflow"""
        for step in workflow.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def _calculate_progress(self, workflow: WorkflowInfo) -> float:
        """คำนวณเปอร์เซ็นต์ความคืบหน้า"""
        if workflow.total_steps == 0:
            return 0.0
        
        completed = workflow.completed_steps + workflow.failed_steps
        return (completed / workflow.total_steps) * 100
    
    def _step_to_dict(self, step: WorkflowStep) -> Dict[str, Any]:
        """แปลง step เป็น dictionary"""
        return {
            "step_id": step.step_id,
            "step_name": step.step_name,
            "module": step.module,
            "status": step.status.value,
            "start_time": step.start_time.isoformat(),
            "end_time": step.end_time.isoformat() if step.end_time else None,
            "duration_ms": step.duration_ms,
            "metadata": step.metadata
        }
    
    def _trigger_callbacks(self, event: str, workflow: WorkflowInfo, step: WorkflowStep = None):
        """เรียก callbacks"""
        for callback in self.callbacks.get(event, []):
            try:
                if step:
                    callback(workflow, step)
                else:
                    callback(workflow)
            except Exception as e:
                print(f"❌ Callback error for {event}: {e}")
    
    def _start_monitoring(self):
        """เริ่ม background monitoring"""
        def monitor_performance():
            while True:
                try:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.performance_metrics["cpu_usage"].append({
                        "timestamp": datetime.now().isoformat(),
                        "value": cpu_percent
                    })
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.performance_metrics["memory_usage"].append({
                        "timestamp": datetime.now().isoformat(),
                        "value": memory.percent
                    })
                    
                    # Disk I/O
                    disk_io = psutil.disk_io_counters()
                    if disk_io:
                        self.performance_metrics["disk_io"].append({
                            "timestamp": datetime.now().isoformat(),
                            "read_bytes": disk_io.read_bytes,
                            "write_bytes": disk_io.write_bytes
                        })
                    
                    # Network I/O
                    network_io = psutil.net_io_counters()
                    if network_io:
                        self.performance_metrics["network_io"].append({
                            "timestamp": datetime.now().isoformat(),
                            "bytes_sent": network_io.bytes_sent,
                            "bytes_recv": network_io.bytes_recv
                        })
                    
                    # จำกัดขนาดของ metrics
                    for key in self.performance_metrics:
                        if len(self.performance_metrics[key]) > 1000:
                            self.performance_metrics[key] = self.performance_metrics[key][-1000:]
                    
                    time.sleep(5)  # อัปเดตทุก 5 วินาที
                    
                except Exception as e:
                    print(f"❌ Performance monitoring error: {e}")
                    time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor_performance, daemon=True)
        monitor_thread.start()


# Global workflow monitor instance
_workflow_monitor = None

def get_workflow_monitor() -> WorkflowMonitor:
    """ดึง global workflow monitor instance"""
    global _workflow_monitor
    if _workflow_monitor is None:
        _workflow_monitor = WorkflowMonitor()
    return _workflow_monitor 