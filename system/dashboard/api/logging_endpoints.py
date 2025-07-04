#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging API Endpoints - FastAPI endpoints สำหรับ real-time logging
ให้ dashboard เข้าถึงข้อมูล log และ workflow แบบ real-time
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import StreamingResponse
from typing import Dict, List, Any, Optional
import json
import asyncio
import time
from datetime import datetime, timedelta
import sys
import os

# เพิ่ม path สำหรับ import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core', 'logging'))

from logger_manager import get_logger_manager, LoggerManager
from workflow_monitor import get_workflow_monitor, WorkflowMonitor, WorkflowStatus, StepStatus
from performance_tracker import get_performance_tracker, PerformanceTracker
from alert_system import get_alert_system, AlertSystem, AlertType, AlertSeverity

router = APIRouter(prefix="/api/logging", tags=["logging"])

# Global instances
logger_manager: LoggerManager = None
workflow_monitor: WorkflowMonitor = None
performance_tracker: PerformanceTracker = None
alert_system: AlertSystem = None

def get_logger_manager_dep():
    """Dependency สำหรับ logger manager"""
    global logger_manager
    if logger_manager is None:
        logger_manager = get_logger_manager()
    return logger_manager

def get_workflow_monitor_dep():
    """Dependency สำหรับ workflow monitor"""
    global workflow_monitor
    if workflow_monitor is None:
        workflow_monitor = get_workflow_monitor()
    return workflow_monitor

def get_performance_tracker_dep():
    """Dependency สำหรับ performance tracker"""
    global performance_tracker
    if performance_tracker is None:
        performance_tracker = get_performance_tracker()
    return performance_tracker

def get_alert_system_dep():
    """Dependency สำหรับ alert system"""
    global alert_system
    if alert_system is None:
        alert_system = get_alert_system()
    return alert_system

# WebSocket connections สำหรับ real-time updates
websocket_connections: List[WebSocket] = []

@router.get("/health")
async def logging_health():
    """ตรวจสอบสถานะของ logging system"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "logger_manager": "active",
                "workflow_monitor": "active", 
                "performance_tracker": "active",
                "alert_system": "active"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logging system error: {str(e)}")

@router.get("/logs/recent")
async def get_recent_logs(
    limit: int = 100,
    module: Optional[str] = None,
    level: Optional[str] = None,
    logger_mgr: LoggerManager = Depends(get_logger_manager_dep)
):
    """ดึง log ล่าสุด"""
    try:
        logs = logger_mgr.get_recent_logs(limit=limit, module=module, level=level)
        return {
            "logs": logs,
            "total": len(logs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting logs: {str(e)}")

@router.get("/logs/stream")
async def stream_logs(
    module: Optional[str] = None,
    level: Optional[str] = None,
    logger_mgr: LoggerManager = Depends(get_logger_manager_dep)
):
    """Stream logs แบบ real-time"""
    async def log_generator():
        try:
            last_check = time.time()
            while True:
                # ดึง logs ใหม่
                current_time = time.time()
                logs = logger_mgr.get_recent_logs(limit=50, module=module, level=level)
                
                # กรอง logs ที่ใหม่กว่า last_check
                new_logs = []
                for log in logs:
                    log_time = datetime.fromisoformat(log["timestamp"]).timestamp()
                    if log_time > last_check:
                        new_logs.append(log)
                
                if new_logs:
                    yield f"data: {json.dumps({'logs': new_logs, 'timestamp': datetime.now().isoformat()})}\n\n"
                
                last_check = current_time
                await asyncio.sleep(1)  # อัปเดตทุก 1 วินาที
                
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        log_generator(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@router.get("/workflows/active")
async def get_active_workflows(
    workflow_mon: WorkflowMonitor = Depends(get_workflow_monitor_dep)
):
    """ดึง workflows ที่กำลังทำงานอยู่"""
    try:
        workflows = workflow_mon.get_active_workflows()
        return {
            "workflows": workflows,
            "total": len(workflows),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting active workflows: {str(e)}")

@router.get("/workflows/history")
async def get_workflow_history(
    limit: int = 50,
    workflow_mon: WorkflowMonitor = Depends(get_workflow_monitor_dep)
):
    """ดึงประวัติ workflows"""
    try:
        workflows = workflow_mon.get_workflow_history(limit=limit)
        return {
            "workflows": workflows,
            "total": len(workflows),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting workflow history: {str(e)}")

@router.get("/workflows/{workflow_id}")
async def get_workflow_status(
    workflow_id: str,
    workflow_mon: WorkflowMonitor = Depends(get_workflow_monitor_dep)
):
    """ดึงสถานะของ workflow เฉพาะ"""
    try:
        status = workflow_mon.get_workflow_status(workflow_id)
        if not status:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting workflow status: {str(e)}")

@router.post("/workflows/create")
async def create_workflow(
    workflow_type: str,
    metadata: Optional[Dict[str, Any]] = None,
    workflow_mon: WorkflowMonitor = Depends(get_workflow_monitor_dep)
):
    """สร้าง workflow ใหม่"""
    try:
        workflow_id = workflow_mon.create_workflow(workflow_type, metadata)
        return {
            "workflow_id": workflow_id,
            "workflow_type": workflow_type,
            "status": "created",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating workflow: {str(e)}")

@router.post("/workflows/{workflow_id}/start")
async def start_workflow(
    workflow_id: str,
    workflow_mon: WorkflowMonitor = Depends(get_workflow_monitor_dep)
):
    """เริ่มต้น workflow"""
    try:
        success = workflow_mon.start_workflow(workflow_id)
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "workflow_id": workflow_id,
            "status": "started",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting workflow: {str(e)}")

@router.post("/workflows/{workflow_id}/steps")
async def add_workflow_step(
    workflow_id: str,
    step_name: str,
    module: str,
    metadata: Optional[Dict[str, Any]] = None,
    workflow_mon: WorkflowMonitor = Depends(get_workflow_monitor_dep)
):
    """เพิ่ม step ใน workflow"""
    try:
        step_id = workflow_mon.add_step(workflow_id, step_name, module, metadata)
        if not step_id:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "workflow_id": workflow_id,
            "step_id": step_id,
            "step_name": step_name,
            "module": module,
            "status": "added",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding workflow step: {str(e)}")

@router.post("/workflows/{workflow_id}/steps/{step_id}/start")
async def start_workflow_step(
    workflow_id: str,
    step_id: str,
    workflow_mon: WorkflowMonitor = Depends(get_workflow_monitor_dep)
):
    """เริ่มต้น workflow step"""
    try:
        success = workflow_mon.start_step(workflow_id, step_id)
        if not success:
            raise HTTPException(status_code=404, detail="Workflow or step not found")
        
        return {
            "workflow_id": workflow_id,
            "step_id": step_id,
            "status": "started",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting workflow step: {str(e)}")

@router.post("/workflows/{workflow_id}/steps/{step_id}/complete")
async def complete_workflow_step(
    workflow_id: str,
    step_id: str,
    duration_ms: Optional[int] = None,
    logs: Optional[List[Dict[str, Any]]] = None,
    workflow_mon: WorkflowMonitor = Depends(get_workflow_monitor_dep)
):
    """เสร็จสิ้น workflow step"""
    try:
        success = workflow_mon.complete_step(workflow_id, step_id, duration_ms, logs)
        if not success:
            raise HTTPException(status_code=404, detail="Workflow or step not found")
        
        return {
            "workflow_id": workflow_id,
            "step_id": step_id,
            "status": "completed",
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing workflow step: {str(e)}")

@router.post("/workflows/{workflow_id}/steps/{step_id}/fail")
async def fail_workflow_step(
    workflow_id: str,
    step_id: str,
    error_message: Optional[str] = None,
    logs: Optional[List[Dict[str, Any]]] = None,
    workflow_mon: WorkflowMonitor = Depends(get_workflow_monitor_dep)
):
    """ล้มเหลว workflow step"""
    try:
        success = workflow_mon.fail_step(workflow_id, step_id, error_message, logs)
        if not success:
            raise HTTPException(status_code=404, detail="Workflow or step not found")
        
        return {
            "workflow_id": workflow_id,
            "step_id": step_id,
            "status": "failed",
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error failing workflow step: {str(e)}")

@router.post("/workflows/{workflow_id}/complete")
async def complete_workflow(
    workflow_id: str,
    workflow_mon: WorkflowMonitor = Depends(get_workflow_monitor_dep)
):
    """เสร็จสิ้น workflow"""
    try:
        success = workflow_mon.complete_workflow(workflow_id)
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing workflow: {str(e)}")

@router.post("/workflows/{workflow_id}/fail")
async def fail_workflow(
    workflow_id: str,
    error_message: Optional[str] = None,
    workflow_mon: WorkflowMonitor = Depends(get_workflow_monitor_dep)
):
    """ล้มเหลว workflow"""
    try:
        success = workflow_mon.fail_workflow(workflow_id, error_message)
        if not success:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return {
            "workflow_id": workflow_id,
            "status": "failed",
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error failing workflow: {str(e)}")

@router.get("/performance/metrics")
async def get_performance_metrics(
    hours: int = 24,
    perf_tracker: PerformanceTracker = Depends(get_performance_tracker_dep)
):
    """ดึง performance metrics"""
    try:
        system_metrics = perf_tracker.get_system_metrics(hours=hours)
        module_metrics = perf_tracker.get_module_metrics(hours=hours)
        performance_alerts = perf_tracker.get_performance_alerts(hours=hours)
        
        return {
            "system_metrics": system_metrics,
            "module_metrics": module_metrics,
            "performance_alerts": performance_alerts,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance metrics: {str(e)}")

@router.get("/performance/summary")
async def get_performance_summary(
    perf_tracker: PerformanceTracker = Depends(get_performance_tracker_dep)
):
    """ดึงสรุปประสิทธิภาพ"""
    try:
        summary = perf_tracker.get_performance_summary()
        return {
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting performance summary: {str(e)}")

@router.post("/performance/track")
async def track_performance(
    module: str,
    operation: str,
    duration_ms: int,
    memory_usage_mb: Optional[float] = None,
    cpu_usage_percent: Optional[float] = None,
    status: str = "completed",
    metadata: Optional[Dict[str, Any]] = None,
    perf_tracker: PerformanceTracker = Depends(get_performance_tracker_dep)
):
    """ติดตามประสิทธิภาพของ module"""
    try:
        perf_tracker.track_module_operation(
            module=module,
            operation=operation,
            duration_ms=duration_ms,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent,
            status=status,
            metadata=metadata
        )
        
        return {
            "module": module,
            "operation": operation,
            "status": "tracked",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking performance: {str(e)}")

@router.get("/alerts/active")
async def get_active_alerts(
    severity: Optional[str] = None,
    alert_type: Optional[str] = None,
    module: Optional[str] = None,
    alert_sys: AlertSystem = Depends(get_alert_system_dep)
):
    """ดึง alerts ที่ยังไม่หมดอายุ"""
    try:
        severity_enum = AlertSeverity(severity) if severity else None
        type_enum = AlertType(alert_type) if alert_type else None
        
        alerts = alert_sys.get_active_alerts(
            severity=severity_enum,
            alert_type=type_enum,
            module=module
        )
        
        return {
            "alerts": alerts,
            "total": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting active alerts: {str(e)}")

@router.get("/alerts/history")
async def get_alert_history(
    hours: int = 24,
    alert_sys: AlertSystem = Depends(get_alert_system_dep)
):
    """ดึงประวัติ alerts"""
    try:
        history = alert_sys.get_alert_history(hours=hours)
        return {
            "history": history,
            "total": len(history),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting alert history: {str(e)}")

@router.get("/alerts/summary")
async def get_alert_summary(
    alert_sys: AlertSystem = Depends(get_alert_system_dep)
):
    """ดึงสรุป alerts"""
    try:
        summary = alert_sys.get_alert_summary()
        return {
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting alert summary: {str(e)}")

@router.post("/alerts/create")
async def create_alert(
    alert_type: str,
    severity: str,
    title: str,
    message: str,
    module: Optional[str] = None,
    workflow_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    auto_dismiss: bool = True,
    dismiss_after_hours: int = 24,
    alert_sys: AlertSystem = Depends(get_alert_system_dep)
):
    """สร้าง alert ใหม่"""
    try:
        type_enum = AlertType(alert_type)
        severity_enum = AlertSeverity(severity)
        
        alert_id = alert_sys.create_alert(
            alert_type=type_enum,
            severity=severity_enum,
            title=title,
            message=message,
            module=module,
            workflow_id=workflow_id,
            metadata=metadata,
            auto_dismiss=auto_dismiss,
            dismiss_after_hours=dismiss_after_hours
        )
        
        return {
            "alert_id": alert_id,
            "status": "created",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating alert: {str(e)}")

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    user: str = "system",
    alert_sys: AlertSystem = Depends(get_alert_system_dep)
):
    """ยืนยันการรับทราบ alert"""
    try:
        success = alert_sys.acknowledge_alert(alert_id, user)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "alert_id": alert_id,
            "status": "acknowledged",
            "user": user,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error acknowledging alert: {str(e)}")

@router.delete("/alerts/{alert_id}")
async def dismiss_alert(
    alert_id: str,
    user: str = "system",
    alert_sys: AlertSystem = Depends(get_alert_system_dep)
):
    """ปิด alert"""
    try:
        success = alert_sys.dismiss_alert(alert_id, user)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "alert_id": alert_id,
            "status": "dismissed",
            "user": user,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error dismissing alert: {str(e)}")

@router.get("/reset/status")
async def get_reset_status(
    logger_mgr: LoggerManager = Depends(get_logger_manager_dep)
):
    """ดึงสถานะ reset ของ log"""
    try:
        status = logger_mgr.get_reset_status()
        return {
            "reset_status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting reset status: {str(e)}")

@router.post("/reset/cleanup")
async def cleanup_logs(
    logger_mgr: LoggerManager = Depends(get_logger_manager_dep)
):
    """ลบ log เก่า"""
    try:
        logger_mgr.cleanup_old_logs()
        return {
            "status": "cleanup_completed",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up logs: {str(e)}")

# WebSocket endpoint สำหรับ real-time updates
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint สำหรับ real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        while True:
            # ส่งข้อมูล real-time ทุก 5 วินาที
            await asyncio.sleep(5)
            
            # ดึงข้อมูลล่าสุด
            data = {
                "type": "real_time_update",
                "timestamp": datetime.now().isoformat(),
                "logs_count": len(logger_manager.get_recent_logs(limit=10)) if logger_manager else 0,
                "active_workflows": len(workflow_monitor.get_active_workflows()) if workflow_monitor else 0,
                "active_alerts": len(alert_system.get_active_alerts()) if alert_system else 0
            }
            
            await websocket.send_text(json.dumps(data))
            
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

# Broadcast function สำหรับส่งข้อมูลไปยัง WebSocket connections ทั้งหมด
async def broadcast_to_websockets(data: Dict[str, Any]):
    """ส่งข้อมูลไปยัง WebSocket connections ทั้งหมด"""
    if not websocket_connections:
        return
    
    message = json.dumps(data)
    disconnected = []
    
    for websocket in websocket_connections:
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"❌ WebSocket broadcast error: {e}")
            disconnected.append(websocket)
    
    # ลบ connections ที่ขาด
    for websocket in disconnected:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket) 