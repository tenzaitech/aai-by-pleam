#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WAWAGOT.AI Flexible API Gateway
API สำหรับเข้าถึง/แก้ไขข้อมูลทุกประเภทแบบยืดหยุ่น
"""
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import sqlite3
import logging
import os
import json
from typing import Dict, Any

app = FastAPI()

ADMIN_TOKEN = os.environ.get('WAWAGOT_ADMIN_TOKEN', 'changeme')
DB_PATH = os.environ.get('WAWAGOT_DB_PATH', 'conversation_logs.db')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('FlexibleAPIGateway')

def check_admin(request: Request):
    token = request.headers.get('Authorization')
    if token != f'Bearer {ADMIN_TOKEN}':
        logger.warning('Unauthorized API access')
        raise HTTPException(status_code=401, detail='Unauthorized')

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get('/conversations')
def get_conversations(limit: int = 100, admin: Any = Depends(check_admin)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return {'conversations': rows}

@app.delete('/conversations/{conv_id}')
def delete_conversation(conv_id: int, admin: Any = Depends(check_admin)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM conversations WHERE id = ?', (conv_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted:
        return {'status': 'deleted', 'id': conv_id}
    else:
        raise HTTPException(status_code=404, detail='Not found')

@app.get('/sessions')
def get_sessions(limit: int = 100, admin: Any = Depends(check_admin)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions ORDER BY last_activity DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return {'sessions': rows}

@app.get('/tags')
def get_tags(limit: int = 100, admin: Any = Depends(check_admin)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tags ORDER BY created_at DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return {'tags': rows}

@app.get('/backup/history')
def get_backup_history(limit: int = 10, admin: Any = Depends(check_admin)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM backup_history ORDER BY created_at DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return {'backup_history': rows}

@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    logger.error(f'Unhandled error: {exc}')
    return JSONResponse(status_code=500, content={'detail': str(exc)})

# เพิ่ม endpoint CRUD อื่นๆ ได้ตามต้องการ 