# WAWAGOT.AI - Integration Patterns Knowledge
# ===============================================================================
# WAWAGOT.AI - System Integration Patterns
# ===============================================================================
# Created: 2024-12-19
# Purpose: Comprehensive integration patterns knowledge
# ===============================================================================

## 🔗 INTEGRATION PATTERNS OVERVIEW
### ===============================================================================

### Integration Strategy
WAWAGOT.AI ใช้รูปแบบการรวมระบบหลายแบบเพื่อให้ระบบทำงานร่วมกันได้อย่างมีประสิทธิภาพ:

1. **API-First Integration** - รวมผ่าน API
2. **Event-Driven Integration** - รวมผ่านเหตุการณ์
3. **Message Queue Integration** - รวมผ่านคิวข้อความ
4. **Database Integration** - รวมผ่านฐานข้อมูล
5. **File System Integration** - รวมผ่านระบบไฟล์
6. **Real-time Integration** - รวมแบบเรียลไทม์

## 🌐 API-FIRST INTEGRATION PATTERNS
### ===============================================================================

### RESTful API Integration
```python
# RESTful API Integration Pattern
class RESTfulAPIIntegration:
    def __init__(self):
        self.base_urls = {
            "ai_service": "https://api.openai.com/v1",
            "automation_service": "https://api.automation.com/v1",
            "knowledge_service": "https://api.knowledge.com/v1",
            "voice_service": "https://api.retellai.com/v2"
        }
        self.session = requests.Session()
        self.rate_limiter = RateLimiter()
    
    async def integrate_with_service(self, service_name, endpoint, method="GET", data=None):
        """รวมกับบริการผ่าน RESTful API"""
        try:
            # ตรวจสอบ rate limit
            if not self.rate_limiter.check_limit(service_name):
                return {"error": "Rate limit exceeded"}
            
            # สร้าง URL
            url = f"{self.base_urls[service_name]}/{endpoint}"
            
            # ส่งคำขอ
            response = await self.make_request(url, method, data)
            
            # ประมวลผลผลลัพธ์
            return self.process_response(response)
            
        except Exception as e:
            return {"error": str(e)}
    
    async def make_request(self, url, method, data=None):
        """ส่งคำขอ HTTP"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.get_api_key()}"
        }
        
        if method.upper() == "GET":
            response = self.session.get(url, headers=headers)
        elif method.upper() == "POST":
            response = self.session.post(url, headers=headers, json=data)
        elif method.upper() == "PUT":
            response = self.session.put(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = self.session.delete(url, headers=headers)
        
        return response
```

### GraphQL Integration
```python
# GraphQL Integration Pattern
class GraphQLIntegration:
    def __init__(self):
        self.graphql_endpoints = {
            "knowledge_graph": "https://api.knowledge.com/graphql",
            "ai_graph": "https://api.ai.com/graphql"
        }
        self.client = GraphQLClient()
    
    async def query_knowledge_graph(self, query, variables=None):
        """สอบถามความรู้ผ่าน GraphQL"""
        try:
            endpoint = self.graphql_endpoints["knowledge_graph"]
            result = await self.client.execute(query, variables, endpoint)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def mutate_knowledge_graph(self, mutation, variables=None):
        """เปลี่ยนแปลงความรู้ผ่าน GraphQL"""
        try:
            endpoint = self.graphql_endpoints["knowledge_graph"]
            result = await self.client.execute(mutation, variables, endpoint)
            return result
        except Exception as e:
            return {"error": str(e)}
```

## 📡 EVENT-DRIVEN INTEGRATION PATTERNS
### ===============================================================================

### Event Bus Integration
```python
# Event Bus Integration Pattern
class EventBusIntegration:
    def __init__(self):
        self.event_bus = EventBus()
        self.event_handlers = {}
        self.event_subscribers = {}
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        """ตั้งค่า event handlers"""
        self.event_handlers = {
            "ai_processing_completed": self.handle_ai_completion,
            "automation_task_finished": self.handle_automation_completion,
            "knowledge_updated": self.handle_knowledge_update,
            "voice_call_ended": self.handle_voice_call_end,
            "system_error": self.handle_system_error
        }
    
    async def publish_event(self, event_type, event_data):
        """เผยแพร่เหตุการณ์"""
        try:
            event = {
                "type": event_type,
                "data": event_data,
                "timestamp": datetime.now().isoformat(),
                "id": str(uuid.uuid4())
            }
            
            # ส่งไปยัง event bus
            await self.event_bus.publish(event)
            
            # เรียก handlers
            if event_type in self.event_handlers:
                await self.event_handlers[event_type](event)
            
            return {"success": True, "event_id": event["id"]}
            
        except Exception as e:
            return {"error": str(e)}
    
    async def subscribe_to_event(self, event_type, handler):
        """สมัครรับเหตุการณ์"""
        try:
            await self.event_bus.subscribe(event_type, handler)
            self.event_subscribers[event_type] = handler
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}
    
    async def handle_ai_completion(self, event):
        """จัดการเมื่อ AI ประมวลผลเสร็จ"""
        # บันทึกผลลัพธ์
        await self.knowledge_manager.store_ai_result(event["data"])
        
        # ส่งการแจ้งเตือน
        await self.notification_system.send_notification(
            "AI processing completed", event["data"]
        )
    
    async def handle_automation_completion(self, event):
        """จัดการเมื่องานอัตโนมัติเสร็จ"""
        # บันทึกผลลัพธ์
        await self.knowledge_manager.store_automation_result(event["data"])
        
        # อัพเดท dashboard
        await self.dashboard_system.update_automation_status(event["data"])
```

### Webhook Integration
```python
# Webhook Integration Pattern
class WebhookIntegration:
    def __init__(self):
        self.webhook_endpoints = {}
        self.webhook_secrets = {}
        self.setup_webhooks()
    
    def setup_webhooks(self):
        """ตั้งค่า webhooks"""
        self.webhook_endpoints = {
            "retell_ai": "/webhooks/retell-ai",
            "openai": "/webhooks/openai",
            "automation": "/webhooks/automation",
            "knowledge": "/webhooks/knowledge"
        }
        
        self.webhook_secrets = {
            "retell_ai": os.getenv("RETELL_WEBHOOK_SECRET"),
            "openai": os.getenv("OPENAI_WEBHOOK_SECRET"),
            "automation": os.getenv("AUTOMATION_WEBHOOK_SECRET"),
            "knowledge": os.getenv("KNOWLEDGE_WEBHOOK_SECRET")
        }
    
    async def handle_webhook(self, webhook_type, payload, signature):
        """จัดการ webhook"""
        try:
            # ตรวจสอบ signature
            if not self.verify_signature(webhook_type, payload, signature):
                return {"error": "Invalid signature"}
            
            # ประมวลผล webhook
            if webhook_type == "retell_ai":
                return await self.handle_retell_webhook(payload)
            elif webhook_type == "openai":
                return await self.handle_openai_webhook(payload)
            elif webhook_type == "automation":
                return await self.handle_automation_webhook(payload)
            elif webhook_type == "knowledge":
                return await self.handle_knowledge_webhook(payload)
            
        except Exception as e:
            return {"error": str(e)}
    
    def verify_signature(self, webhook_type, payload, signature):
        """ตรวจสอบ signature"""
        secret = self.webhook_secrets.get(webhook_type)
        if not secret:
            return False
        
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    async def handle_retell_webhook(self, payload):
        """จัดการ Retell.AI webhook"""
        # ประมวลผลข้อมูลการโทร
        call_data = payload.get("call_data", {})
        
        # บันทึกข้อมูลการโทร
        await self.knowledge_manager.store_call_data(call_data)
        
        # อัพเดท dashboard
        await self.dashboard_system.update_call_status(call_data)
        
        return {"success": True}
```

## 📨 MESSAGE QUEUE INTEGRATION PATTERNS
### ===============================================================================

### Message Queue Integration
```python
# Message Queue Integration Pattern
class MessageQueueIntegration:
    def __init__(self):
        self.message_queues = {
            "ai_tasks": AIQueue(),
            "automation_tasks": AutomationQueue(),
            "knowledge_updates": KnowledgeQueue(),
            "voice_tasks": VoiceQueue()
        }
        self.message_processors = {}
        self.setup_processors()
    
    def setup_processors(self):
        """ตั้งค่า message processors"""
        self.message_processors = {
            "ai_tasks": self.process_ai_task,
            "automation_tasks": self.process_automation_task,
            "knowledge_updates": self.process_knowledge_update,
            "voice_tasks": self.process_voice_task
        }
    
    async def send_message(self, queue_name, message):
        """ส่งข้อความไปยังคิว"""
        try:
            if queue_name in self.message_queues:
                message_id = await self.message_queues[queue_name].send(message)
                return {"success": True, "message_id": message_id}
            else:
                return {"error": f"Queue {queue_name} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    async def receive_message(self, queue_name):
        """รับข้อความจากคิว"""
        try:
            if queue_name in self.message_queues:
                message = await self.message_queues[queue_name].receive()
                return message
            else:
                return {"error": f"Queue {queue_name} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    async def process_message(self, queue_name, message):
        """ประมวลผลข้อความ"""
        try:
            if queue_name in self.message_processors:
                result = await self.message_processors[queue_name](message)
                return result
            else:
                return {"error": f"Processor for {queue_name} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    async def process_ai_task(self, message):
        """ประมวลผลงาน AI"""
        task_data = message.get("data", {})
        
        # ประมวลผลด้วย AI
        ai_result = await self.ai_system.process(task_data)
        
        # บันทึกผลลัพธ์
        await self.knowledge_manager.store_ai_result(ai_result)
        
        return {"success": True, "result": ai_result}
    
    async def process_automation_task(self, message):
        """ประมวลผลงานอัตโนมัติ"""
        task_data = message.get("data", {})
        
        # ทำงานอัตโนมัติ
        automation_result = await self.automation_system.execute(task_data)
        
        # บันทึกผลลัพธ์
        await self.knowledge_manager.store_automation_result(automation_result)
        
        return {"success": True, "result": automation_result}
```

## 🗄️ DATABASE INTEGRATION PATTERNS
### ===============================================================================

### Database Integration
```python
# Database Integration Pattern
class DatabaseIntegration:
    def __init__(self):
        self.databases = {
            "primary": SupabaseDatabase(),
            "cache": RedisDatabase(),
            "file_storage": FileDatabase(),
            "analytics": AnalyticsDatabase()
        }
        self.connection_pool = ConnectionPool()
        self.setup_connections()
    
    def setup_connections(self):
        """ตั้งค่าการเชื่อมต่อฐานข้อมูล"""
        for db_name, db_instance in self.databases.items():
            connection = self.connection_pool.get_connection(db_name)
            db_instance.set_connection(connection)
    
    async def write_data(self, database_name, table_name, data):
        """เขียนข้อมูลลงฐานข้อมูล"""
        try:
            if database_name in self.databases:
                result = await self.databases[database_name].write(table_name, data)
                return {"success": True, "result": result}
            else:
                return {"error": f"Database {database_name} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    async def read_data(self, database_name, table_name, query=None):
        """อ่านข้อมูลจากฐานข้อมูล"""
        try:
            if database_name in self.databases:
                result = await self.databases[database_name].read(table_name, query)
                return {"success": True, "result": result}
            else:
                return {"error": f"Database {database_name} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    async def update_data(self, database_name, table_name, data, condition):
        """อัพเดทข้อมูลในฐานข้อมูล"""
        try:
            if database_name in self.databases:
                result = await self.databases[database_name].update(table_name, data, condition)
                return {"success": True, "result": result}
            else:
                return {"error": f"Database {database_name} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    async def delete_data(self, database_name, table_name, condition):
        """ลบข้อมูลจากฐานข้อมูล"""
        try:
            if database_name in self.databases:
                result = await self.databases[database_name].delete(table_name, condition)
                return {"success": True, "result": result}
            else:
                return {"error": f"Database {database_name} not found"}
        except Exception as e:
            return {"error": str(e)}
```

### Supabase Integration
```python
# Supabase Integration Pattern
class SupabaseIntegration:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.client = create_client(self.supabase_url, self.supabase_key)
    
    async def insert_data(self, table_name, data):
        """เพิ่มข้อมูลลง Supabase"""
        try:
            result = self.client.table(table_name).insert(data).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"error": str(e)}
    
    async def select_data(self, table_name, query=None):
        """เลือกข้อมูลจาก Supabase"""
        try:
            if query:
                result = self.client.table(table_name).select(query).execute()
            else:
                result = self.client.table(table_name).select("*").execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"error": str(e)}
    
    async def update_data(self, table_name, data, condition):
        """อัพเดทข้อมูลใน Supabase"""
        try:
            result = self.client.table(table_name).update(data).eq(condition).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"error": str(e)}
    
    async def delete_data(self, table_name, condition):
        """ลบข้อมูลจาก Supabase"""
        try:
            result = self.client.table(table_name).delete().eq(condition).execute()
            return {"success": True, "data": result.data}
        except Exception as e:
            return {"error": str(e)}
```

## 📁 FILE SYSTEM INTEGRATION PATTERNS
### ===============================================================================

### File System Integration
```python
# File System Integration Pattern
class FileSystemIntegration:
    def __init__(self):
        self.file_storage = {
            "local": LocalFileStorage(),
            "cloud": CloudFileStorage(),
            "backup": BackupFileStorage()
        }
        self.file_processors = {}
        self.setup_processors()
    
    def setup_processors(self):
        """ตั้งค่า file processors"""
        self.file_processors = {
            "text": self.process_text_file,
            "image": self.process_image_file,
            "audio": self.process_audio_file,
            "video": self.process_video_file,
            "data": self.process_data_file
        }
    
    async def save_file(self, storage_type, file_path, content, file_type=None):
        """บันทึกไฟล์"""
        try:
            if storage_type in self.file_storage:
                result = await self.file_storage[storage_type].save(file_path, content)
                
                # ประมวลผลไฟล์ถ้าจำเป็น
                if file_type and file_type in self.file_processors:
                    await self.file_processors[file_type](file_path, content)
                
                return {"success": True, "file_path": result}
            else:
                return {"error": f"Storage type {storage_type} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    async def load_file(self, storage_type, file_path):
        """โหลดไฟล์"""
        try:
            if storage_type in self.file_storage:
                content = await self.file_storage[storage_type].load(file_path)
                return {"success": True, "content": content}
            else:
                return {"error": f"Storage type {storage_type} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    async def delete_file(self, storage_type, file_path):
        """ลบไฟล์"""
        try:
            if storage_type in self.file_storage:
                result = await self.file_storage[storage_type].delete(file_path)
                return {"success": True, "result": result}
            else:
                return {"error": f"Storage type {storage_type} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    async def process_text_file(self, file_path, content):
        """ประมวลผลไฟล์ข้อความ"""
        # วิเคราะห์ข้อความ
        text_analysis = await self.ai_system.analyze_text(content)
        
        # บันทึกการวิเคราะห์
        await self.knowledge_manager.store_text_analysis(file_path, text_analysis)
    
    async def process_image_file(self, file_path, content):
        """ประมวลผลไฟล์ภาพ"""
        # วิเคราะห์ภาพ
        image_analysis = await self.ai_system.analyze_image(content)
        
        # บันทึกการวิเคราะห์
        await self.knowledge_manager.store_image_analysis(file_path, image_analysis)
```

## ⚡ REAL-TIME INTEGRATION PATTERNS
### ===============================================================================

### WebSocket Integration
```python
# WebSocket Integration Pattern
class WebSocketIntegration:
    def __init__(self):
        self.websocket_connections = {}
        self.websocket_handlers = {}
        self.setup_handlers()
    
    def setup_handlers(self):
        """ตั้งค่า WebSocket handlers"""
        self.websocket_handlers = {
            "dashboard_updates": self.handle_dashboard_update,
            "ai_progress": self.handle_ai_progress,
            "automation_status": self.handle_automation_status,
            "voice_call_status": self.handle_voice_call_status
        }
    
    async def connect_websocket(self, connection_id, connection_type):
        """เชื่อมต่อ WebSocket"""
        try:
            websocket = await self.create_websocket_connection(connection_type)
            self.websocket_connections[connection_id] = websocket
            return {"success": True, "connection_id": connection_id}
        except Exception as e:
            return {"error": str(e)}
    
    async def send_message(self, connection_id, message_type, data):
        """ส่งข้อความผ่าน WebSocket"""
        try:
            if connection_id in self.websocket_connections:
                websocket = self.websocket_connections[connection_id]
                message = {
                    "type": message_type,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send(json.dumps(message))
                return {"success": True}
            else:
                return {"error": f"Connection {connection_id} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    async def handle_dashboard_update(self, data):
        """จัดการการอัพเดท dashboard"""
        # อัพเดท dashboard
        await self.dashboard_system.update_real_time(data)
        
        # ส่งการแจ้งเตือน
        await self.notification_system.send_dashboard_notification(data)
    
    async def handle_ai_progress(self, data):
        """จัดการความคืบหน้า AI"""
        # อัพเดทสถานะ AI
        await self.ai_system.update_progress(data)
        
        # ส่งการแจ้งเตือน
        await self.notification_system.send_ai_progress_notification(data)
```

### Server-Sent Events Integration
```python
# Server-Sent Events Integration Pattern
class SSEIntegration:
    def __init__(self):
        self.sse_connections = {}
        self.event_types = {
            "system_status": self.send_system_status,
            "ai_updates": self.send_ai_updates,
            "automation_updates": self.send_automation_updates,
            "knowledge_updates": self.send_knowledge_updates
        }
    
    async def create_sse_connection(self, client_id, event_types=None):
        """สร้าง SSE connection"""
        try:
            connection = {
                "client_id": client_id,
                "event_types": event_types or ["system_status"],
                "created_at": datetime.now().isoformat()
            }
            
            self.sse_connections[client_id] = connection
            return {"success": True, "client_id": client_id}
        except Exception as e:
            return {"error": str(e)}
    
    async def send_event(self, client_id, event_type, data):
        """ส่ง event ผ่าน SSE"""
        try:
            if client_id in self.sse_connections:
                connection = self.sse_connections[client_id]
                
                if event_type in connection["event_types"]:
                    event_data = {
                        "type": event_type,
                        "data": data,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # ส่ง event
                    await self.send_sse_event(client_id, event_data)
                    return {"success": True}
                else:
                    return {"error": f"Event type {event_type} not subscribed"}
            else:
                return {"error": f"Client {client_id} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    async def send_system_status(self, client_id, data):
        """ส่งสถานะระบบ"""
        await self.send_event(client_id, "system_status", data)
    
    async def send_ai_updates(self, client_id, data):
        """ส่งการอัพเดท AI"""
        await self.send_event(client_id, "ai_updates", data)
```

## 🔄 CROSS-SYSTEM INTEGRATION PATTERNS
### ===============================================================================

### Cross-System Integration
```python
# Cross-System Integration Pattern
class CrossSystemIntegration:
    def __init__(self):
        self.system_connectors = {
            "ai_to_automation": AItoAutomationConnector(),
            "automation_to_knowledge": AutomationToKnowledgeConnector(),
            "knowledge_to_voice": KnowledgeToVoiceConnector(),
            "voice_to_dashboard": VoiceToDashboardConnector()
        }
        self.integration_workflows = {}
        self.setup_workflows()
    
    def setup_workflows(self):
        """ตั้งค่า integration workflows"""
        self.integration_workflows = {
            "ai_automation_workflow": self.ai_automation_workflow,
            "automation_knowledge_workflow": self.automation_knowledge_workflow,
            "knowledge_voice_workflow": self.knowledge_voice_workflow,
            "voice_dashboard_workflow": self.voice_dashboard_workflow
        }
    
    async def execute_workflow(self, workflow_name, data):
        """ทำงาน workflow"""
        try:
            if workflow_name in self.integration_workflows:
                result = await self.integration_workflows[workflow_name](data)
                return {"success": True, "result": result}
            else:
                return {"error": f"Workflow {workflow_name} not found"}
        except Exception as e:
            return {"error": str(e)}
    
    async def ai_automation_workflow(self, data):
        """AI to Automation workflow"""
        # 1. AI ประมวลผลข้อมูล
        ai_result = await self.ai_system.process(data)
        
        # 2. ส่งไปยัง automation
        automation_result = await self.automation_system.execute(ai_result)
        
        # 3. บันทึกผลลัพธ์
        await self.knowledge_manager.store_workflow_result(
            "ai_automation", {"ai_result": ai_result, "automation_result": automation_result}
        )
        
        return {"ai_result": ai_result, "automation_result": automation_result}
    
    async def automation_knowledge_workflow(self, data):
        """Automation to Knowledge workflow"""
        # 1. ทำงานอัตโนมัติ
        automation_result = await self.automation_system.execute(data)
        
        # 2. บันทึกความรู้
        knowledge_result = await self.knowledge_manager.store_automation_result(automation_result)
        
        # 3. วิเคราะห์ความรู้
        analysis_result = await self.knowledge_manager.analyze_knowledge(knowledge_result)
        
        return {"automation_result": automation_result, "knowledge_result": knowledge_result, "analysis": analysis_result}
```

## 🎯 INTEGRATION BEST PRACTICES
### ===============================================================================

### Best Practices
1. **Loose Coupling** - หลวมการเชื่อมต่อ
2. **High Cohesion** - ความสอดคล้องสูง
3. **Error Handling** - จัดการข้อผิดพลาด
4. **Retry Logic** - ตรรกะการลองใหม่
5. **Circuit Breaker** - วงจรเบรกเกอร์
6. **Rate Limiting** - จำกัดอัตรา
7. **Monitoring** - การติดตาม
8. **Logging** - การบันทึก

### Error Handling Patterns
```python
# Error Handling Pattern
class ErrorHandlingPattern:
    def __init__(self):
        self.error_handlers = {}
        self.retry_config = {}
        self.circuit_breaker = CircuitBreaker()
    
    async def handle_integration_error(self, integration_type, error, context=None):
        """จัดการข้อผิดพลาดการรวม"""
        try:
            # บันทึกข้อผิดพลาด
            await self.log_error(integration_type, error, context)
            
            # ตรวจสอบ retry logic
            if self.should_retry(integration_type, error):
                return await self.retry_integration(integration_type, context)
            
            # ตรวจสอบ circuit breaker
            if self.circuit_breaker.is_open(integration_type):
                return {"error": "Circuit breaker is open"}
            
            # เรียก error handler
            if integration_type in self.error_handlers:
                return await self.error_handlers[integration_type](error, context)
            
            return {"error": str(error)}
            
        except Exception as e:
            return {"error": f"Error handling failed: {str(e)}"}
```

# ===============================================================================
# END OF INTEGRATION PATTERNS KNOWLEDGE
# =============================================================================== 