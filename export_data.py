#!/usr/bin/env python
"""
Export all data from the database to JSON fixtures for migration.
This will export data from users, catalog, builds, and marketplace apps.

Usage: python export_data.py
"""
import os
import sys
import subprocess

def main():
    # Apps to export (in dependency order)
    apps_to_export = ['users', 'catalog', 'builds', 'marketplace']
    
    print("=" * 60)
    print("BuildForge Data Export Tool")
    print("=" * 60)
    print("\nThis will export all your data to JSON files.\n")
    
    exported_files = []
    
    for app in apps_to_export:
        output_file = f'{app}_data.json'
        cmd = ['python', 'manage.py', 'dumpdata', app, '--indent', '2', '-o', output_file]
        
        print(f"📦 Exporting {app}...", end=' ')
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Check if file was created and has content
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                if file_size > 10:  # More than just empty array
                    print(f"✓ ({file_size:,} bytes)")
                    exported_files.append(output_file)
                else:
                    print(f"⚠️  (empty)")
            else:
                print(f"❌ (failed)")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e.stderr}")
            continue
    
    print("\n" + "=" * 60)
    print("✅ Export Complete!")
    print("=" * 60)
    print("\nFiles created:")
    for file in exported_files:
        print(f"  📄 {file}")
    
    print("\n⚠️  IMPORTANT: Keep these files safe!")
    print("   You'll need them to import data on Render.com")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
