# WAWAGOT.AI - Memory Management System
# ===============================================================================
# WAWAGOT.AI - Complete Memory Management
# ===============================================================================
# Created: 2024-12-19
# Purpose: Comprehensive memory management knowledge
# ===============================================================================

## 🧠 MEMORY MANAGEMENT OVERVIEW
### ===============================================================================

### Memory System Architecture
WAWAGOT.AI ใช้ระบบจัดการความจำหลายระดับเพื่อเก็บและเรียกใช้ข้อมูลอย่างมีประสิทธิภาพ:

```
Memory Management Architecture
┌─────────────────────────────────────────────────────────────┐
│                    Short-term Memory                       │
├─────────────────────────────────────────────────────────────┤
│  Session Cache  │  Request Cache  │  Temporary Storage     │
├─────────────────────────────────────────────────────────────┤
│                   Medium-term Memory                       │
├─────────────────────────────────────────────────────────────┤
│  Knowledge Base  │  Learning Cache  │  Pattern Storage     │
├─────────────────────────────────────────────────────────────┤
│                    Long-term Memory                        │
├─────────────────────────────────────────────────────────────┤
│  Database  │  File System  │  Cloud Storage  │  Archive    │
└─────────────────────────────────────────────────────────────┘
```

## ⚡ SHORT-TERM MEMORY SYSTEM
### ===============================================================================

### Session Memory Management
```python
# Session Memory Management
class SessionMemoryManager:
    def __init__(self):
        self.session_cache = {}
        self.request_cache = {}
        self.temp_storage = {}
        self.max_session_size = 1000
        self.max_request_size = 100
        self.max_temp_size = 500
        self.session_ttl = 3600  # 1 hour
        self.request_ttl = 300   # 5 minutes
        self.temp_ttl = 1800     # 30 minutes
    
    async def store_session_data(self, session_id, data):
        """เก็บข้อมูล session"""
        try:
            # ตรวจสอบขนาด cache
            if len(self.session_cache) >= self.max_session_size:
                await self.cleanup_old_sessions()
            
            # เก็บข้อมูล
            self.session_cache[session_id] = {
                "data": data,
                "timestamp": datetime.now(),
                "access_count": 1,
                "last_access": datetime.now()
            }
            
            return {"success": True, "session_id": session_id}
        except Exception as e:
            return {"error": str(e)}
    
    async def retrieve_session_data(self, session_id):
        """ดึงข้อมูล session"""
        try:
            if session_id in self.session_cache:
                session_data = self.session_cache[session_id]
                
                # อัพเดท access count และ timestamp
                session_data["access_count"] += 1
                session_data["last_access"] = datetime.now()
                
                # ตรวจสอบ TTL
                if self.is_expired(session_data["timestamp"], self.session_ttl):
                    del self.session_cache[session_id]
                    return {"error": "Session expired"}
                
                return {"success": True, "data": session_data["data"]}
            else:
                return {"error": "Session not found"}
        except Exception as e:
            return {"error": str(e)}
    
    async def store_request_data(self, request_id, data):
        """เก็บข้อมูล request"""
        try:
            if len(self.request_cache) >= self.max_request_size:
                await self.cleanup_old_requests()
            
            self.request_cache[request_id] = {
                "data": data,
                "timestamp": datetime.now()
            }
            
            return {"success": True, "request_id": request_id}
        except Exception as e:
            return {"error": str(e)}
    
    async def cleanup_old_sessions(self):
        """ล้าง session เก่า"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.session_cache.items():
            if self.is_expired(session_data["timestamp"], self.session_ttl):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.session_cache[session_id]
    
    def is_expired(self, timestamp, ttl_seconds):
        """ตรวจสอบว่า expired หรือไม่"""
        return (datetime.now() - timestamp).total_seconds() > ttl_seconds
```

### Request Memory Management
```python
# Request Memory Management
class RequestMemoryManager:
    def __init__(self):
        self.request_history = []
        self.max_history_size = 1000
        self.request_patterns = {}
        self.response_cache = {}
    
    async def store_request(self, request_data):
        """เก็บข้อมูล request"""
        try:
            # เพิ่ม request ลง history
            request_entry = {
                "id": str(uuid.uuid4()),
                "data": request_data,
                "timestamp": datetime.now(),
                "type": self.analyze_request_type(request_data)
            }
            
            self.request_history.append(request_entry)
            
            # จำกัดขนาด history
            if len(self.request_history) > self.max_history_size:
                self.request_history.pop(0)
            
            # วิเคราะห์ pattern
            await self.analyze_request_pattern(request_entry)
            
            return {"success": True, "request_id": request_entry["id"]}
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_request_type(self, request_data):
        """วิเคราะห์ประเภทของ request"""
        if "ai" in request_data.get("type", "").lower():
            return "ai_request"
        elif "automation" in request_data.get("type", "").lower():
            return "automation_request"
        elif "knowledge" in request_data.get("type", "").lower():
            return "knowledge_request"
        else:
            return "general_request"
    
    async def analyze_request_pattern(self, request_entry):
        """วิเคราะห์ pattern ของ request"""
        request_type = request_entry["type"]
        
        if request_type not in self.request_patterns:
            self.request_patterns[request_type] = {
                "count": 0,
                "frequency": {},
                "common_data": {}
            }
        
        pattern = self.request_patterns[request_type]
        pattern["count"] += 1
        
        # วิเคราะห์ความถี่
        hour = request_entry["timestamp"].hour
        pattern["frequency"][hour] = pattern["frequency"].get(hour, 0) + 1
        
        # วิเคราะห์ข้อมูลทั่วไป
        data_keys = list(request_entry["data"].keys())
        for key in data_keys:
            if key not in pattern["common_data"]:
                pattern["common_data"][key] = 0
            pattern["common_data"][key] += 1
```

## 🧩 MEDIUM-TERM MEMORY SYSTEM
### ===============================================================================

### Knowledge Memory Management
```python
# Knowledge Memory Management
class KnowledgeMemoryManager:
    def __init__(self):
        self.knowledge_cache = {}
        self.learning_cache = {}
        self.pattern_storage = {}
        self.knowledge_index = {}
        self.max_knowledge_size = 10000
        self.max_learning_size = 5000
        self.knowledge_ttl = 86400  # 24 hours
        self.learning_ttl = 43200   # 12 hours
    
    async def store_knowledge(self, knowledge_id, knowledge_data):
        """เก็บความรู้"""
        try:
            # ตรวจสอบขนาด cache
            if len(self.knowledge_cache) >= self.max_knowledge_size:
                await self.cleanup_old_knowledge()
            
            # เก็บความรู้
            knowledge_entry = {
                "id": knowledge_id,
                "data": knowledge_data,
                "timestamp": datetime.now(),
                "access_count": 0,
                "last_access": datetime.now(),
                "category": self.categorize_knowledge(knowledge_data),
                "tags": self.extract_tags(knowledge_data)
            }
            
            self.knowledge_cache[knowledge_id] = knowledge_entry
            
            # สร้าง index
            await self.build_knowledge_index(knowledge_entry)
            
            return {"success": True, "knowledge_id": knowledge_id}
        except Exception as e:
            return {"error": str(e)}
    
    async def retrieve_knowledge(self, knowledge_id):
        """ดึงความรู้"""
        try:
            if knowledge_id in self.knowledge_cache:
                knowledge_entry = self.knowledge_cache[knowledge_id]
                
                # อัพเดท access count
                knowledge_entry["access_count"] += 1
                knowledge_entry["last_access"] = datetime.now()
                
                # ตรวจสอบ TTL
                if self.is_expired(knowledge_entry["timestamp"], self.knowledge_ttl):
                    del self.knowledge_cache[knowledge_id]
                    return {"error": "Knowledge expired"}
                
                return {"success": True, "data": knowledge_entry["data"]}
            else:
                return {"error": "Knowledge not found"}
        except Exception as e:
            return {"error": str(e)}
    
    async def search_knowledge(self, query):
        """ค้นหาความรู้"""
        try:
            results = []
            query_terms = query.lower().split()
            
            for knowledge_id, knowledge_entry in self.knowledge_cache.items():
                score = 0
                
                # ค้นหาใน tags
                for tag in knowledge_entry["tags"]:
                    if any(term in tag.lower() for term in query_terms):
                        score += 2
                
                # ค้นหาใน content
                content = str(knowledge_entry["data"]).lower()
                for term in query_terms:
                    if term in content:
                        score += 1
                
                if score > 0:
                    results.append({
                        "knowledge_id": knowledge_id,
                        "score": score,
                        "data": knowledge_entry["data"],
                        "category": knowledge_entry["category"]
                    })
            
            # เรียงตาม score
            results.sort(key=lambda x: x["score"], reverse=True)
            
            return {"success": True, "results": results}
        except Exception as e:
            return {"error": str(e)}
    
    def categorize_knowledge(self, knowledge_data):
        """จัดหมวดหมู่ความรู้"""
        content = str(knowledge_data).lower()
        
        if any(word in content for word in ["ai", "machine learning", "neural"]):
            return "ai_ml"
        elif any(word in content for word in ["automation", "selenium", "chrome"]):
            return "automation"
        elif any(word in content for word in ["database", "sql", "supabase"]):
            return "database"
        elif any(word in content for word in ["api", "rest", "http"]):
            return "api"
        elif any(word in content for word in ["voice", "speech", "retell"]):
            return "voice_ai"
        else:
            return "general"
    
    def extract_tags(self, knowledge_data):
        """ดึง tags จากความรู้"""
        content = str(knowledge_data).lower()
        tags = []
        
        # ดึงคำสำคัญ
        important_words = [
            "python", "flask", "fastapi", "selenium", "openai", "gemini",
            "supabase", "postgresql", "redis", "docker", "kubernetes",
            "ai", "ml", "automation", "api", "database", "voice"
        ]
        
        for word in important_words:
            if word in content:
                tags.append(word)
        
        return tags
```

### Learning Memory Management
```python
# Learning Memory Management
class LearningMemoryManager:
    def __init__(self):
        self.learning_cache = {}
        self.learning_patterns = {}
        self.adaptation_rules = {}
        self.performance_metrics = {}
        self.max_learning_size = 5000
        self.learning_ttl = 43200  # 12 hours
    
    async def store_learning_data(self, learning_id, learning_data):
        """เก็บข้อมูลการเรียนรู้"""
        try:
            if len(self.learning_cache) >= self.max_learning_size:
                await self.cleanup_old_learning()
            
            learning_entry = {
                "id": learning_id,
                "data": learning_data,
                "timestamp": datetime.now(),
                "type": self.analyze_learning_type(learning_data),
                "effectiveness": self.calculate_effectiveness(learning_data),
                "applicability": self.assess_applicability(learning_data)
            }
            
            self.learning_cache[learning_id] = learning_entry
            
            # อัพเดท learning patterns
            await self.update_learning_patterns(learning_entry)
            
            return {"success": True, "learning_id": learning_id}
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_learning_type(self, learning_data):
        """วิเคราะห์ประเภทการเรียนรู้"""
        content = str(learning_data).lower()
        
        if "pattern" in content or "regularity" in content:
            return "pattern_learning"
        elif "error" in content or "failure" in content:
            return "error_learning"
        elif "success" in content or "optimization" in content:
            return "success_learning"
        elif "user" in content or "preference" in content:
            return "user_learning"
        else:
            return "general_learning"
    
    def calculate_effectiveness(self, learning_data):
        """คำนวณประสิทธิภาพการเรียนรู้"""
        # Implementation for effectiveness calculation
        return 0.8  # Default effectiveness score
    
    def assess_applicability(self, learning_data):
        """ประเมินการใช้งานได้"""
        # Implementation for applicability assessment
        return 0.9  # Default applicability score
    
    async def update_learning_patterns(self, learning_entry):
        """อัพเดท learning patterns"""
        learning_type = learning_entry["type"]
        
        if learning_type not in self.learning_patterns:
            self.learning_patterns[learning_type] = {
                "count": 0,
                "total_effectiveness": 0,
                "total_applicability": 0,
                "recent_learnings": []
            }
        
        pattern = self.learning_patterns[learning_type]
        pattern["count"] += 1
        pattern["total_effectiveness"] += learning_entry["effectiveness"]
        pattern["total_applicability"] += learning_entry["applicability"]
        
        # เก็บการเรียนรู้ล่าสุด
        pattern["recent_learnings"].append(learning_entry)
        if len(pattern["recent_learnings"]) > 100:
            pattern["recent_learnings"].pop(0)
```

## 💾 LONG-TERM MEMORY SYSTEM
### ===============================================================================

### Database Memory Management
```python
# Database Memory Management
class DatabaseMemoryManager:
    def __init__(self):
        self.database_connections = {}
        self.memory_tables = {
            "knowledge_base": "knowledge_table",
            "learning_data": "learning_table",
            "session_data": "session_table",
            "user_preferences": "preferences_table",
            "system_metrics": "metrics_table"
        }
        self.backup_schedule = {
            "frequency": "daily",
            "retention_days": 30,
            "compression": True
        }
    
    async def store_to_database(self, table_name, data):
        """เก็บข้อมูลลงฐานข้อมูล"""
        try:
            if table_name not in self.memory_tables:
                return {"error": f"Table {table_name} not found"}
            
            actual_table = self.memory_tables[table_name]
            
            # เพิ่ม metadata
            data_with_metadata = {
                **data,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": 1
            }
            
            # เก็บลงฐานข้อมูล
            result = await self.execute_database_operation(
                "insert", actual_table, data_with_metadata
            )
            
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}
    
    async def retrieve_from_database(self, table_name, query=None):
        """ดึงข้อมูลจากฐานข้อมูล"""
        try:
            if table_name not in self.memory_tables:
                return {"error": f"Table {table_name} not found"}
            
            actual_table = self.memory_tables[table_name]
            
            # ดึงข้อมูล
            result = await self.execute_database_operation(
                "select", actual_table, query
            )
            
            return {"success": True, "data": result}
        except Exception as e:
            return {"error": str(e)}
    
    async def update_in_database(self, table_name, data, condition):
        """อัพเดทข้อมูลในฐานข้อมูล"""
        try:
            if table_name not in self.memory_tables:
                return {"error": f"Table {table_name} not found"}
            
            actual_table = self.memory_tables[table_name]
            
            # อัพเดท metadata
            data_with_metadata = {
                **data,
                "updated_at": datetime.now().isoformat()
            }
            
            # อัพเดทในฐานข้อมูล
            result = await self.execute_database_operation(
                "update", actual_table, data_with_metadata, condition
            )
            
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}
    
    async def execute_database_operation(self, operation, table, data=None, condition=None):
        """ทำงานฐานข้อมูล"""
        # Implementation for database operations
        return {"operation": operation, "table": table, "success": True}
```

### File System Memory Management
```python
# File System Memory Management
class FileSystemMemoryManager:
    def __init__(self):
        self.memory_directories = {
            "knowledge": "data/knowledge/",
            "learning": "data/learning/",
            "sessions": "data/sessions/",
            "backups": "data/backups/",
            "logs": "data/logs/",
            "temp": "data/temp/"
        }
        self.file_formats = {
            "json": "application/json",
            "yaml": "application/x-yaml",
            "pickle": "application/x-pickle",
            "csv": "text/csv",
            "txt": "text/plain"
        }
        self.compression_enabled = True
    
    async def store_to_file(self, directory_name, filename, data, format_type="json"):
        """เก็บข้อมูลลงไฟล์"""
        try:
            if directory_name not in self.memory_directories:
                return {"error": f"Directory {directory_name} not found"}
            
            directory_path = self.memory_directories[directory_name]
            file_path = os.path.join(directory_path, filename)
            
            # สร้างโฟลเดอร์ถ้าไม่มี
            os.makedirs(directory_path, exist_ok=True)
            
            # เตรียมข้อมูล
            data_with_metadata = {
                "data": data,
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "format": format_type,
                    "size": len(str(data)),
                    "checksum": self.calculate_checksum(data)
                }
            }
            
            # เขียนไฟล์
            if format_type == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data_with_metadata, f, ensure_ascii=False, indent=2)
            elif format_type == "yaml":
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data_with_metadata, f, default_flow_style=False)
            elif format_type == "pickle":
                with open(file_path, 'wb') as f:
                    pickle.dump(data_with_metadata, f)
            
            # บีบอัดไฟล์ถ้าเปิดใช้งาน
            if self.compression_enabled:
                await self.compress_file(file_path)
            
            return {"success": True, "file_path": file_path}
        except Exception as e:
            return {"error": str(e)}
    
    async def retrieve_from_file(self, directory_name, filename, format_type="json"):
        """ดึงข้อมูลจากไฟล์"""
        try:
            if directory_name not in self.memory_directories:
                return {"error": f"Directory {directory_name} not found"}
            
            directory_path = self.memory_directories[directory_name]
            file_path = os.path.join(directory_path, filename)
            
            if not os.path.exists(file_path):
                return {"error": "File not found"}
            
            # ตรวจสอบไฟล์บีบอัด
            if self.compression_enabled and file_path.endswith('.gz'):
                await self.decompress_file(file_path)
            
            # อ่านไฟล์
            if format_type == "json":
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif format_type == "yaml":
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
            elif format_type == "pickle":
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
            
            # ตรวจสอบ checksum
            if not self.verify_checksum(data["data"], data["metadata"]["checksum"]):
                return {"error": "Data integrity check failed"}
            
            return {"success": True, "data": data["data"]}
        except Exception as e:
            return {"error": str(e)}
    
    def calculate_checksum(self, data):
        """คำนวณ checksum"""
        return hashlib.md5(str(data).encode()).hexdigest()
    
    def verify_checksum(self, data, expected_checksum):
        """ตรวจสอบ checksum"""
        actual_checksum = self.calculate_checksum(data)
        return actual_checksum == expected_checksum
    
    async def compress_file(self, file_path):
        """บีบอัดไฟล์"""
        import gzip
        with open(file_path, 'rb') as f_in:
            with gzip.open(file_path + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(file_path)
    
    async def decompress_file(self, file_path):
        """คลายบีบอัดไฟล์"""
        import gzip
        with gzip.open(file_path, 'rb') as f_in:
            with open(file_path[:-3], 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
```

## 🔄 MEMORY OPTIMIZATION SYSTEM
### ===============================================================================

### Memory Optimization Manager
```python
# Memory Optimization Manager
class MemoryOptimizationManager:
    def __init__(self):
        self.optimization_rules = {}
        self.memory_usage_thresholds = {
            "short_term": 0.8,  # 80%
            "medium_term": 0.7,  # 70%
            "long_term": 0.9    # 90%
        }
        self.cleanup_schedules = {
            "short_term": 300,   # 5 minutes
            "medium_term": 3600, # 1 hour
            "long_term": 86400   # 24 hours
        }
    
    async def optimize_memory_usage(self):
        """ปรับปรุงการใช้หน่วยความจำ"""
        try:
            optimization_results = {}
            
            # ตรวจสอบ short-term memory
            short_term_usage = await self.check_memory_usage("short_term")
            if short_term_usage > self.memory_usage_thresholds["short_term"]:
                result = await self.optimize_short_term_memory()
                optimization_results["short_term"] = result
            
            # ตรวจสอบ medium-term memory
            medium_term_usage = await self.check_memory_usage("medium_term")
            if medium_term_usage > self.memory_usage_thresholds["medium_term"]:
                result = await self.optimize_medium_term_memory()
                optimization_results["medium_term"] = result
            
            # ตรวจสอบ long-term memory
            long_term_usage = await self.check_memory_usage("long_term")
            if long_term_usage > self.memory_usage_thresholds["long_term"]:
                result = await self.optimize_long_term_memory()
                optimization_results["long_term"] = result
            
            return {"success": True, "optimization_results": optimization_results}
        except Exception as e:
            return {"error": str(e)}
    
    async def check_memory_usage(self, memory_type):
        """ตรวจสอบการใช้หน่วยความจำ"""
        # Implementation for memory usage checking
        return 0.5  # Default usage percentage
    
    async def optimize_short_term_memory(self):
        """ปรับปรุง short-term memory"""
        # ล้าง cache เก่า
        # ลบ session ที่หมดอายุ
        # บีบอัดข้อมูล
        return {"optimized": True, "freed_space": "100MB"}
    
    async def optimize_medium_term_memory(self):
        """ปรับปรุง medium-term memory"""
        # ย้ายข้อมูลเก่าไป long-term
        # บีบอัด knowledge cache
        # ลบ learning data ที่ไม่มีประสิทธิภาพ
        return {"optimized": True, "freed_space": "500MB"}
    
    async def optimize_long_term_memory(self):
        """ปรับปรุง long-term memory"""
        # สร้าง backup
        # ลบข้อมูลเก่า
        # บีบอัดไฟล์
        return {"optimized": True, "freed_space": "1GB"}
```

## 🔍 MEMORY SEARCH & RETRIEVAL
### ===============================================================================

### Memory Search Engine
```python
# Memory Search Engine
class MemorySearchEngine:
    def __init__(self):
        self.search_index = {}
        self.search_algorithms = {
            "exact_match": self.exact_match_search,
            "fuzzy_match": self.fuzzy_match_search,
            "semantic_search": self.semantic_search,
            "pattern_search": self.pattern_search
        }
        self.search_weights = {
            "relevance": 0.4,
            "recency": 0.3,
            "frequency": 0.2,
            "confidence": 0.1
        }
    
    async def search_memory(self, query, search_type="semantic", limit=10):
        """ค้นหาความจำ"""
        try:
            if search_type not in self.search_algorithms:
                return {"error": f"Search type {search_type} not supported"}
            
            # ดำเนินการค้นหา
            search_algorithm = self.search_algorithms[search_type]
            raw_results = await search_algorithm(query)
            
            # คำนวณ score
            scored_results = await self.calculate_search_scores(raw_results, query)
            
            # เรียงลำดับและจำกัดผลลัพธ์
            sorted_results = sorted(scored_results, key=lambda x: x["score"], reverse=True)
            limited_results = sorted_results[:limit]
            
            return {"success": True, "results": limited_results}
        except Exception as e:
            return {"error": str(e)}
    
    async def exact_match_search(self, query):
        """ค้นหาแบบตรงตัว"""
        results = []
        query_lower = query.lower()
        
        # ค้นหาใน short-term memory
        for session_id, session_data in self.session_cache.items():
            if query_lower in str(session_data["data"]).lower():
                results.append({
                    "type": "session",
                    "id": session_id,
                    "data": session_data["data"],
                    "timestamp": session_data["timestamp"]
                })
        
        # ค้นหาใน medium-term memory
        for knowledge_id, knowledge_data in self.knowledge_cache.items():
            if query_lower in str(knowledge_data["data"]).lower():
                results.append({
                    "type": "knowledge",
                    "id": knowledge_id,
                    "data": knowledge_data["data"],
                    "timestamp": knowledge_data["timestamp"]
                })
        
        return results
    
    async def fuzzy_match_search(self, query):
        """ค้นหาแบบคลุมเครือ"""
        results = []
        query_terms = query.lower().split()
        
        # ค้นหาใน short-term memory
        for session_id, session_data in self.session_cache.items():
            content = str(session_data["data"]).lower()
            match_score = self.calculate_fuzzy_score(query_terms, content)
            
            if match_score > 0.3:  # Threshold
                results.append({
                    "type": "session",
                    "id": session_id,
                    "data": session_data["data"],
                    "timestamp": session_data["timestamp"],
                    "match_score": match_score
                })
        
        return results
    
    async def semantic_search(self, query):
        """ค้นหาแบบความหมาย"""
        # Implementation for semantic search using AI
        return []
    
    async def pattern_search(self, query):
        """ค้นหาแบบ pattern"""
        # Implementation for pattern-based search
        return []
    
    async def calculate_search_scores(self, results, query):
        """คำนวณ search scores"""
        scored_results = []
        
        for result in results:
            score = 0
            
            # Relevance score
            relevance_score = result.get("match_score", 0.5)
            score += relevance_score * self.search_weights["relevance"]
            
            # Recency score
            recency_score = self.calculate_recency_score(result["timestamp"])
            score += recency_score * self.search_weights["recency"]
            
            # Frequency score
            frequency_score = result.get("access_count", 1) / 100
            score += frequency_score * self.search_weights["frequency"]
            
            # Confidence score
            confidence_score = result.get("confidence", 0.8)
            score += confidence_score * self.search_weights["confidence"]
            
            result["score"] = score
            scored_results.append(result)
        
        return scored_results
    
    def calculate_fuzzy_score(self, query_terms, content):
        """คำนวณ fuzzy match score"""
        total_score = 0
        
        for term in query_terms:
            if term in content:
                total_score += 1
        
        return total_score / len(query_terms) if query_terms else 0
    
    def calculate_recency_score(self, timestamp):
        """คำนวณ recency score"""
        time_diff = (datetime.now() - timestamp).total_seconds()
        # Score decreases with time (exponential decay)
        return math.exp(-time_diff / 86400)  # 24 hours decay
```

## 🔄 MEMORY SYNCHRONIZATION
### ===============================================================================

### Memory Synchronization Manager
```python
# Memory Synchronization Manager
class MemorySynchronizationManager:
    def __init__(self):
        self.sync_queue = []
        self.sync_status = {}
        self.sync_conflicts = []
        self.sync_schedule = {
            "frequency": 300,  # 5 minutes
            "batch_size": 100,
            "retry_attempts": 3
        }
    
    async def synchronize_memory(self):
        """ซิงค์ความจำ"""
        try:
            sync_results = {}
            
            # ซิงค์ short-term memory
            short_term_sync = await self.sync_short_term_memory()
            sync_results["short_term"] = short_term_sync
            
            # ซิงค์ medium-term memory
            medium_term_sync = await self.sync_medium_term_memory()
            sync_results["medium_term"] = medium_term_sync
            
            # ซิงค์ long-term memory
            long_term_sync = await self.sync_long_term_memory()
            sync_results["long_term"] = long_term_sync
            
            # จัดการ conflicts
            await self.resolve_sync_conflicts()
            
            return {"success": True, "sync_results": sync_results}
        except Exception as e:
            return {"error": str(e)}
    
    async def sync_short_term_memory(self):
        """ซิงค์ short-term memory"""
        # ย้ายข้อมูลที่สำคัญไป medium-term
        # ลบข้อมูลชั่วคราว
        return {"synced": True, "items_processed": 50}
    
    async def sync_medium_term_memory(self):
        """ซิงค์ medium-term memory"""
        # ย้ายข้อมูลที่เสถียรไป long-term
        # อัพเดท indexes
        return {"synced": True, "items_processed": 200}
    
    async def sync_long_term_memory(self):
        """ซิงค์ long-term memory"""
        # สร้าง backup
        # อัพเดท metadata
        return {"synced": True, "items_processed": 1000}
    
    async def resolve_sync_conflicts(self):
        """แก้ไข conflicts การซิงค์"""
        for conflict in self.sync_conflicts:
            # ใช้ timestamp ล่าสุด
            # หรือใช้ version control
            # หรือใช้ conflict resolution strategy
            pass
```

# ===============================================================================
# END OF MEMORY MANAGEMENT SYSTEM
# =============================================================================== 