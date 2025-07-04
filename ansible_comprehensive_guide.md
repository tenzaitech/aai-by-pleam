# Ansible Comprehensive Study Guide - คู่มือการศึกษาอย่างละเอียด

## 📋 **Ansible คืออะไร**

### 🎯 **คำนิยาม**
- **Ansible** เป็น Configuration Management และ Automation Tool ที่ใช้ Python
- เป็น **Agentless** - ไม่ต้องติดตั้ง agent บน target machines
- ใช้ **SSH** เป็นหลักในการเชื่อมต่อ
- ใช้ **YAML** เป็นภาษาสำหรับเขียน Playbooks
- พัฒนาโดย Red Hat (ปัจจุบันเป็นส่วนหนึ่งของ IBM)

### 🔑 **Key Features**
- **Simple** - เรียนรู้ง่าย ใช้ YAML syntax
- **Agentless** - ไม่ต้องติดตั้ง software เพิ่มเติมบน target
- **Powerful** - รองรับ automation ที่ซับซ้อน
- **Secure** - ใช้ SSH และไม่ต้องเปิด port เพิ่มเติม
- **Extensible** - สามารถเขียน custom modules ได้

---

## 🏗️ **Architecture ของ Ansible**

### **1. Control Node (Management Node)**
```
┌─────────────────────────────────┐
│        Control Node             │
│  ┌─────────────────────────┐    │
│  │     Ansible Engine      │    │
│  │                         │    │
│  │  • Playbooks           │    │
│  │  • Inventory           │    │
│  │  • Modules             │    │
│  │  • Plugins             │    │
│  └─────────────────────────┘    │
└─────────────────────────────────┘
```

### **2. Managed Nodes (Target Hosts)**
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Web Server    │  │  Database       │  │   Load Balancer │
│                 │  │  Server         │  │                 │
│  • SSH          │  │  • SSH          │  │  • SSH          │
│  • Python       │  │  • Python       │  │  • Python       │
│  • No Agent     │  │  • No Agent     │  │  • No Agent     │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### **3. Communication Flow**
```
Control Node → SSH → Managed Node 1
              SSH → Managed Node 2
              SSH → Managed Node 3
```

---

## 📦 **การติดตั้ง Ansible**

### **1. ติดตั้งบน Control Node**

#### **Ubuntu/Debian:**
```bash
# Update package list
sudo apt update

# Install Ansible
sudo apt install ansible

# Verify installation
ansible --version
```

#### **CentOS/RHEL:**
```bash
# Install EPEL repository
sudo yum install epel-release

# Install Ansible
sudo yum install ansible

# Verify installation
ansible --version
```

#### **macOS:**
```bash
# Using Homebrew
brew install ansible

# Verify installation
ansible --version
```

#### **Windows:**
```bash
# Using pip
pip install ansible

# Or using WSL
wsl --install
# Then follow Ubuntu instructions
```

### **2. ติดตั้งบน Managed Nodes**
- **ไม่ต้องติดตั้ง Ansible** (Agentless)
- ต้องมี **SSH** และ **Python** เท่านั้น
- Python มักจะติดตั้งมาพร้อมกับ Linux distributions

---

## 📁 **โครงสร้างไฟล์และ Directory**

### **1. Ansible Configuration**
```bash
# Global config file
/etc/ansible/ansible.cfg

# User config file
~/.ansible.cfg

# Project config file
./ansible.cfg
```

### **2. Inventory Structure**
```
inventory/
├── hosts                    # Main inventory file
├── group_vars/             # Variables for groups
│   ├── webservers.yml
│   └── databases.yml
├── host_vars/              # Variables for specific hosts
│   ├── web1.example.com.yml
│   └── db1.example.com.yml
└── production/             # Environment-specific inventory
    └── hosts
```

### **3. Playbook Structure**
```
playbooks/
├── site.yml                # Main playbook
├── webservers.yml          # Web server configuration
├── databases.yml           # Database configuration
├── roles/                  # Roles directory
│   ├── common/
│   ├── webserver/
│   └── database/
└── vars/                   # Variables
    ├── main.yml
    └── secrets.yml
```

---

## 🔧 **Core Components**

### **1. Inventory (Hosts File)**

#### **Basic Inventory:**
```ini
# /etc/ansible/hosts
[webservers]
web1.example.com
web2.example.com

[databases]
db1.example.com
db2.example.com

[all:vars]
ansible_user=admin
ansible_ssh_private_key_file=~/.ssh/id_rsa
```

#### **Advanced Inventory:**
```yaml
# inventory.yml
all:
  children:
    webservers:
      hosts:
        web1.example.com:
          ansible_host: 192.168.1.10
          http_port: 80
        web2.example.com:
          ansible_host: 192.168.1.11
          http_port: 8080
      vars:
        nginx_version: 1.18.0
    
    databases:
      hosts:
        db1.example.com:
          ansible_host: 192.168.1.20
        db2.example.com:
          ansible_host: 192.168.1.21
      vars:
        mysql_version: 8.0
    
    loadbalancers:
      hosts:
        lb1.example.com:
          ansible_host: 192.168.1.30
```

### **2. Playbooks**

#### **Basic Playbook:**
```yaml
# playbook.yml
---
- name: Configure web servers
  hosts: webservers
  become: yes
  tasks:
    - name: Install nginx
      apt:
        name: nginx
        state: present
        update_cache: yes
    
    - name: Start nginx service
      service:
        name: nginx
        state: started
        enabled: yes
    
    - name: Copy nginx configuration
      copy:
        src: nginx.conf
        dest: /etc/nginx/nginx.conf
        notify: restart nginx
  
  handlers:
    - name: restart nginx
      service:
        name: nginx
        state: restarted
```

#### **Advanced Playbook:**
```yaml
# advanced_playbook.yml
---
- name: Configure production environment
  hosts: all
  gather_facts: yes
  become: yes
  
  vars:
    app_name: myapp
    app_version: "1.0.0"
    database_host: "{{ hostvars[groups['databases'][0]]['ansible_default_ipv4']['address'] }}"
  
  pre_tasks:
    - name: Update package cache
      apt:
        update_cache: yes
      when: ansible_os_family == "Debian"
    
    - name: Install required packages
      yum:
        name: "{{ item }}"
        state: present
      loop:
        - python3
        - python3-pip
        - git
      when: ansible_os_family == "RedHat"
  
  tasks:
    - name: Create application directory
      file:
        path: "/var/www/{{ app_name }}"
        state: directory
        owner: www-data
        group: www-data
        mode: '0755'
    
    - name: Deploy application
      git:
        repo: "https://github.com/user/{{ app_name }}.git"
        dest: "/var/www/{{ app_name }}"
        version: "{{ app_version }}"
        force: yes
    
    - name: Install Python dependencies
      pip:
        requirements: "/var/www/{{ app_name }}/requirements.txt"
        virtualenv: "/var/www/{{ app_name }}/venv"
    
    - name: Configure application
      template:
        src: app.conf.j2
        dest: "/var/www/{{ app_name }}/config/app.conf"
        owner: www-data
        group: www-data
        mode: '0644'
      notify: restart application
  
  handlers:
    - name: restart application
      systemd:
        name: "{{ app_name }}"
        state: restarted
        daemon_reload: yes
      when: ansible_service_mgr == "systemd"
```

### **3. Roles**

#### **Role Structure:**
```
roles/
└── webserver/
    ├── defaults/
    │   └── main.yml          # Default variables
    ├── files/                # Static files
    │   ├── nginx.conf
    │   └── index.html
    ├── handlers/
    │   └── main.yml          # Handlers
    ├── meta/
    │   └── main.yml          # Role metadata
    ├── tasks/
    │   └── main.yml          # Main tasks
    ├── templates/            # Jinja2 templates
    │   └── nginx.conf.j2
    └── vars/
        └── main.yml          # Role variables
```

#### **Role Example:**
```yaml
# roles/webserver/tasks/main.yml
---
- name: Install nginx
  package:
    name: nginx
    state: present

- name: Configure nginx
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    notify: restart nginx

- name: Start nginx
  service:
    name: nginx
    state: started
    enabled: yes
```

```yaml
# roles/webserver/defaults/main.yml
---
nginx_port: 80
nginx_root: /var/www/html
nginx_user: www-data
```

```yaml
# roles/webserver/handlers/main.yml
---
- name: restart nginx
  service:
    name: nginx
    state: restarted
```

### **4. Variables**

#### **Variable Types:**
```yaml
# 1. Global Variables (group_vars/all.yml)
---
app_name: myapp
app_version: "1.0.0"
database_host: localhost

# 2. Group Variables (group_vars/webservers.yml)
---
nginx_port: 80
nginx_worker_processes: 4

# 3. Host Variables (host_vars/web1.example.com.yml)
---
nginx_port: 8080
server_name: web1.example.com

# 4. Playbook Variables
---
- name: Configure web servers
  hosts: webservers
  vars:
    nginx_port: 80
    app_name: myapp
  tasks:
    - name: Configure nginx
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        vars:
          port: "{{ nginx_port }}"
```

### **5. Templates (Jinja2)**

#### **Template Example:**
```jinja2
# templates/nginx.conf.j2
user {{ nginx_user }};
worker_processes {{ nginx_worker_processes }};

events {
    worker_connections {{ nginx_worker_connections }};
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    server {
        listen {{ nginx_port }};
        server_name {{ server_name }};
        
        root {{ nginx_root }};
        index index.html index.htm;
        
        location / {
            try_files $uri $uri/ =404;
        }
        
        {% if ssl_enabled %}
        location /secure {
            proxy_pass https://backend;
        }
        {% endif %}
    }
}
```

---

## 🚀 **การใช้งาน Ansible**

### **1. Basic Commands**

#### **Ping Test:**
```bash
# Test connectivity to all hosts
ansible all -m ping

# Test specific group
ansible webservers -m ping

# Test specific host
ansible web1.example.com -m ping
```

#### **Ad-hoc Commands:**
```bash
# Check uptime on all servers
ansible all -a "uptime"

# Install package
ansible webservers -m apt -a "name=nginx state=present" --become

# Copy file
ansible webservers -m copy -a "src=/local/file dest=/remote/file"

# Execute command with sudo
ansible all -a "systemctl status nginx" --become
```

#### **Run Playbook:**
```bash
# Run playbook
ansible-playbook playbook.yml

# Run with specific inventory
ansible-playbook -i inventory/hosts playbook.yml

# Run with extra variables
ansible-playbook playbook.yml -e "app_version=2.0.0"

# Run with verbose output
ansible-playbook playbook.yml -v

# Run with check mode (dry run)
ansible-playbook playbook.yml --check
```

### **2. Advanced Usage**

#### **Conditional Execution:**
```yaml
- name: Install nginx on Ubuntu
  apt:
    name: nginx
    state: present
  when: ansible_os_family == "Debian"

- name: Install nginx on CentOS
  yum:
    name: nginx
    state: present
  when: ansible_os_family == "RedHat"
```

#### **Loops:**
```yaml
- name: Install multiple packages
  package:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - mysql-server
    - php-fpm

- name: Create multiple users
  user:
    name: "{{ item.name }}"
    uid: "{{ item.uid }}"
    group: "{{ item.group }}"
  loop:
    - { name: 'john', uid: '1001', group: 'developers' }
    - { name: 'jane', uid: '1002', group: 'developers' }
```

#### **Error Handling:**
```yaml
- name: Attempt risky operation
  command: /risky/command
  ignore_errors: yes
  register: result

- name: Handle failure
  debug:
    msg: "Operation failed: {{ result.stderr }}"
  when: result.rc != 0
```

---

## 🔒 **Security Best Practices**

### **1. SSH Configuration**
```bash
# Use SSH keys instead of passwords
ansible_ssh_private_key_file: ~/.ssh/id_rsa

# Disable password authentication
ansible_ssh_pass: ""

# Use specific user
ansible_user: ansible
```

### **2. Vault for Secrets**
```bash
# Create encrypted file
ansible-vault create secrets.yml

# Edit encrypted file
ansible-vault edit secrets.yml

# Run playbook with vault
ansible-playbook playbook.yml --ask-vault-pass

# Use vault password file
ansible-playbook playbook.yml --vault-password-file ~/.vault_pass
```

### **3. Privilege Escalation**
```yaml
- name: Configure system
  hosts: all
  become: yes
  become_method: sudo
  become_user: root
  tasks:
    - name: Install package
      package:
        name: nginx
        state: present
```

---

## 📊 **Monitoring and Logging**

### **1. Ansible Logging**
```ini
# ansible.cfg
[defaults]
log_path = /var/log/ansible.log
display_skipped_hosts = False
display_ok_hosts = False
```

### **2. Callback Plugins**
```yaml
# Enable callback plugins
callback_whitelist = profile_tasks, timer, log_plays
```

### **3. Performance Monitoring**
```bash
# Check execution time
time ansible-playbook playbook.yml

# Use profile_tasks callback
ansible-playbook playbook.yml -c profile_tasks
```

---

## 🔧 **Custom Modules**

### **1. Module Structure:**
```python
#!/usr/bin/python3
# -*- coding: utf-8 -*-

DOCUMENTATION = r'''
---
module: custom_module
short_description: Custom module description
description:
    - Detailed description of what the module does
options:
    name:
        description:
            - Name parameter
        required: yes
        type: str
'''

EXAMPLES = r'''
- name: Use custom module
  custom_module:
    name: example
'''

RETURN = r'''
changed:
    description: Whether the module made changes
    type: bool
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule

def run_module():
    module_args = dict(
        name=dict(type='str', required=True)
    )
    
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    
    result = dict(
        changed=False,
        msg=''
    )
    
    # Module logic here
    
    module.exit_json(**result)

if __name__ == '__main__':
    run_module()
```

---

## 🌐 **Ansible Tower/AWX**

### **1. AWX Features:**
- **Web UI** สำหรับจัดการ Ansible
- **Role-based Access Control**
- **Job Templates**
- **Scheduling**
- **Inventory Management**
- **Credential Management**

### **2. Installation:**
```bash
# Install AWX
git clone https://github.com/ansible/awx.git
cd awx/installer
ansible-playbook -i inventory install.yml
```

---

## 📈 **Performance Optimization**

### **1. Parallel Execution:**
```yaml
# ansible.cfg
[defaults]
forks = 20
host_key_checking = False
```

### **2. Fact Caching:**
```yaml
# ansible.cfg
[defaults]
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 86400
```

### **3. SSH Optimization:**
```yaml
# ansible.cfg
[ssh_connection]
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
pipelining = True
```

---

## 🧪 **Testing and Validation**

### **1. Molecule Testing:**
```yaml
# molecule/default/molecule.yml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: instance
    image: ubuntu:20.04
provisioner:
  name: ansible
verifier:
  name: ansible
```

### **2. Ansible Lint:**
```bash
# Install ansible-lint
pip install ansible-lint

# Run linting
ansible-lint playbook.yml
```

---

## 📚 **Resources และ Documentation**

### **1. Official Documentation:**
- [Ansible Documentation](https://docs.ansible.com/)
- [Ansible Galaxy](https://galaxy.ansible.com/)
- [Ansible GitHub](https://github.com/ansible/ansible)

### **2. Best Practices:**
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [Ansible Security](https://docs.ansible.com/ansible/latest/user_guide/security.html)

### **3. Community:**
- [Ansible Community](https://www.ansible.com/community)
- [Red Hat Ansible](https://www.ansible.com/)

---

## 💾 **บันทึกในความทรงจำ**

✅ **Ansible คือ Configuration Management และ Automation Tool**  
✅ **Agentless Architecture** - ไม่ต้องติดตั้ง agent บน target  
✅ **ใช้ SSH และ YAML** - เรียนรู้ง่าย ใช้งานสะดวก  
✅ **Core Components** - Inventory, Playbooks, Roles, Variables, Templates  
✅ **Security Features** - Vault, SSH keys, Privilege escalation  
✅ **Performance Optimization** - Parallel execution, Fact caching  
✅ **Testing Tools** - Molecule, Ansible Lint  
✅ **Enterprise Features** - AWX/Ansible Tower  

**ความมั่นใจ: 98%** - Ansible เป็นเครื่องมือที่ทรงพลังสำหรับ Infrastructure as Code และ Automation

---

## 🎯 **Use Cases ใน WAWAGOT System**

### **1. Infrastructure Provisioning:**
- ติดตั้งและ configure servers
- Deploy applications
- Manage configurations

### **2. Continuous Deployment:**
- Automated deployment pipeline
- Environment management
- Rollback procedures

### **3. Configuration Management:**
- System hardening
- Security patches
- Compliance management

### **4. Disaster Recovery:**
- Backup automation
- Recovery procedures
- Environment replication 