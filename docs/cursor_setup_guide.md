# Cursor Setup Guide - WAWAGOT.AI

## 📋 Overview
คู่มือการตั้งค่า Cursor IDE สำหรับโปรเจกต์ WAWAGOT.AI

## 🚀 Quick Setup

### 1. Install Required Extensions
```bash
# Python extensions
ext install ms-python.python
ext install ms-python.vscode-pylance
ext install ms-python.black-formatter

# Git extensions
ext install eamodio.gitlens
ext install mhutchie.git-graph

# AI extensions
ext install GitHub.copilot
ext install GitHub.copilot-chat

# Database extensions
ext install cweijan.vscode-postgresql-client2
```

### 2. Configure Settings
สร้างไฟล์ `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "./.venv-gpu/Scripts/python.exe",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/.venv*": true,
    "**/node_modules": true
  },
  "search.exclude": {
    "**/.venv*": true,
    "**/__pycache__": true,
    "**/logs": true,
    "**/data/*.json": true
  }
}
```

### 3. Custom Resources Index

#### Project Structure
```
wawagot.ai/
├── core/                    # Core system components
├── config/                  # Configuration files
├── data/                    # Data storage
├── docs/                    # Documentation
├── pleamthinking/           # Personal notes and memory
├── system/                  # System monitoring
├── tools/                   # Utility tools
└── tests/                   # Test files
```

#### Key Files Reference
- `.cursorrules` - AI assistant configuration
- `.cursor/mcp.json` - MCP server configuration
- `mcp_flask_server.py` - MCP server implementation
- `system_health_checker.py` - System health monitoring
- `pleamthinking/` - Personal memory and notes

#### Environment Variables
สร้างไฟล์ `.env` จาก `.env.template`

#### Database Schema
- Supabase tables: users, conversations, memory, system_logs
- Local files: pleamthinking/*.txt

## 🔧 Advanced Configuration

### Custom Snippets
สร้างไฟล์ `.vscode/snippets/python.json`:
```json
{
  "Thai Function": {
    "prefix": "thai_func",
    "body": [
      "def ${1:function_name}(${2:parameters}):",
      "    \"\"\"",
      "    ${3:Thai description}",
      "    \"\"\"",
      "    try:",
      "        ${4:pass}",
      "    except Exception as e:",
      "        logger.error(f\"Error in ${1:function_name}: {e}\")",
      "        raise",
      "    return ${5:result}"
    ]
  }
}
```

### Task Configuration
สร้างไฟล์ `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start MCP Server",
      "type": "shell",
      "command": "python",
      "args": ["mcp_flask_server.py"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "new"
      }
    },
    {
      "label": "Start Dashboard",
      "type": "shell",
      "command": "python",
      "args": ["dashboard/app.py"],
      "group": "build",
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "new"
      }
    },
    {
      "label": "Health Check",
      "type": "shell",
      "command": "python",
      "args": ["system_health_checker.py"],
      "group": "test"
    }
  ]
}
```

## 🎯 Usage Tips

### 1. AI Assistant Commands
- `/memory` - Access personal memory
- `/health` - Check system health
- `/docs` - Generate documentation
- `/test` - Run tests
- `/deploy` - Deployment commands

### 2. Keyboard Shortcuts
- `Ctrl+Shift+P` - Command palette
- `Ctrl+Shift+E` - Explorer
- `Ctrl+Shift+G` - Git
- `Ctrl+Shift+D` - Debug
- `Ctrl+Shift+X` - Extensions

### 3. Git Integration
- Use GitLens for advanced git features
- Configure git hooks for pre-commit checks
- Use conventional commits format

## 🔍 Troubleshooting

### MCP Server Issues
1. Check if server is running: `curl http://localhost:5001/tools`
2. Verify `.cursor/mcp.json` configuration
3. Restart Cursor after configuration changes

### Python Environment Issues
1. Verify virtual environment activation
2. Check Python interpreter path
3. Install missing dependencies

### Performance Issues
1. Exclude unnecessary folders from search
2. Use workspace-specific settings
3. Disable unused extensions

## 📚 Additional Resources

- [Cursor Documentation](https://cursor.sh/docs)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Python Best Practices](https://docs.python-guide.org/)
- [Supabase Documentation](https://supabase.com/docs)

## 🔄 Maintenance

### Regular Tasks
- Update dependencies monthly
- Review and clean up logs
- Backup personal memory
- Update documentation

### Performance Monitoring
- Monitor memory usage
- Check system health
- Review error logs
- Optimize configurations 