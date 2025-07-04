"""
Restore Tool - เครื่องมือ restore แบบ command line
"""
import argparse
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.restore_controller import RestoreController

def main():
    parser = argparse.ArgumentParser(description='Restore Tool')
    parser.add_argument('backup_path', help='Backup path to restore')
    parser.add_argument('target_path', help='Target path to restore to')
    
    args = parser.parse_args()
    
    controller = RestoreController()
    result = controller.restore_system(args.backup_path, args.target_path)
    
    if result:
        print("Restore successful!")
    else:
        print("Restore failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
