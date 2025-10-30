#!/usr/bin/env python3
"""
Release Package Creator for Southwest Airlines Tech Ops SPC Dashboard v2.1
Creates a comprehensive ZIP package with all documentation and assets
"""

import os
import zipfile
import shutil
import datetime
from pathlib import Path

def create_release_package():
    """Create comprehensive release package for v2.1"""
    
    # Package information
    version = "2.1"
    release_date = datetime.date.today().strftime("%Y-%m-%d")
    package_name = f"Southwest_Airlines_Tech_Ops_SPC_Dashboard_v{version}_Offline_Complete"
    
    print(f"Creating release package: {package_name}")
    print(f"Version: {version}")
    print(f"Date: {release_date}")
    print("-" * 60)
    
    # Create temporary directory structure
    temp_dir = Path(package_name)
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    temp_dir.mkdir()
    
    # Core application files
    core_files = [
        "dashboard_standalone.html",
        "server.py", 
        "spc_processor.py",
        "load_actual_data.py",
        "test_offline_functionality.py",
        "START_DASHBOARD.bat",
        "start_dashboard.sh",
        "SW Tech Ops logo.png"
    ]
    
    print("📦 Copying core application files...")
    for file in core_files:
        if os.path.exists(file):
            shutil.copy2(file, temp_dir / file)
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️  {file} (not found)")
    
    # JavaScript libraries
    print("\n📚 Copying JavaScript libraries...")
    js_dir = temp_dir / "js"
    js_dir.mkdir()
    
    if os.path.exists("js/plotly-2.27.0.min.js"):
        shutil.copy2("js/plotly-2.27.0.min.js", js_dir / "plotly-2.27.0.min.js")
        file_size = os.path.getsize("js/plotly-2.27.0.min.js") / (1024 * 1024)
        print(f"  ✅ plotly-2.27.0.min.js ({file_size:.1f}MB)")
    else:
        print("  ❌ plotly-2.27.0.min.js (CRITICAL - not found)")
    
    # Images and branding
    print("\n🎨 Copying images and branding...")
    images_dir = temp_dir / "images"
    if os.path.exists("images"):
        shutil.copytree("images", images_dir)
        image_count = len(list(images_dir.glob("*")))
        print(f"  ✅ {image_count} image files copied")
    else:
        print("  ⚠️  images directory not found")
    
    # Input data files
    print("\n📊 Copying sample data...")
    input_dir = temp_dir / "input"
    if os.path.exists("input"):
        shutil.copytree("input", input_dir)
        data_count = len(list(input_dir.glob("*.csv")))
        print(f"  ✅ {data_count} CSV data files copied")
    else:
        print("  ⚠️  input directory not found")
    
    # Documentation
    print("\n📚 Copying documentation...")
    docs_dir = temp_dir / "Documentation"
    docs_dir.mkdir()
    
    doc_files = [
        "README.md",
        "TECHNICAL_SPEC.html",
        "PRD_Product_Requirements.html", 
        "PROJECT_MANAGEMENT.html",
        "FUNCTIONAL_SPEC.html",
        "Explainer_File.html",
        "DEVELOPER_GUIDE.md",
        "SPC_Rules_and_Odds.html",
        "csv_format_checker.html"
    ]
    
    for file in doc_files:
        if os.path.exists(file):
            shutil.copy2(file, docs_dir / file)
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️  {file} (not found)")
    
    # Release notes and changelogs
    print("\n📋 Copying release notes...")
    release_dir = temp_dir / "Release_Notes"
    release_dir.mkdir()
    
    release_files = [
        "RELEASE_NOTES_v2.1.md",
        "CHANGELOG_v2.1.md",
        "RELEASE_NOTES_v2.0.md",
        "RELEASE_NOTES_v1.7.md",
        "RELEASE_NOTES_v1.6.md",
        "CHANGELOG_v1.7.md",
        "CHANGELOG_v1.6.md",
        "CHANGELOG_v1.5.1.md",
        "CHANGELOG_v1.5.md"
    ]
    
    for file in release_files:
        if os.path.exists(file):
            shutil.copy2(file, release_dir / file)
            print(f"  ✅ {file}")
        else:
            print(f"  ⚠️  {file} (not found)")
    
    # Create README for the package
    print("\n📝 Creating package README...")
    package_readme = temp_dir / "README_PACKAGE.md"
    with open(package_readme, 'w', encoding='utf-8') as f:
        f.write(f"""# Southwest Airlines Tech Ops SPC Dashboard v{version}

**True Offline Capability Release**

## 🚀 Quick Start

### Windows
1. Double-click `START_DASHBOARD.bat`
2. Browser opens automatically to `http://localhost:8000`

### Mac/Linux  
1. Open Terminal in this folder
2. Run: `chmod +x start_dashboard.sh && ./start_dashboard.sh`
3. Browser opens automatically to `http://localhost:8000`

## 📁 Package Contents

### Core Application
- `dashboard_standalone.html` - Main dashboard application
- `server.py` - Local Python HTTP server
- `spc_processor.py` - SPC calculation engine
- `load_actual_data.py` - Data loading utilities
- `test_offline_functionality.py` - Offline validation script

### JavaScript Libraries (Offline)
- `js/plotly-2.27.0.min.js` - Local Plotly.js library (3.4MB)

### Sample Data
- `input/` - Sample CSV files and test datasets

### Documentation
- `Documentation/` - Complete technical and user documentation
- `Release_Notes/` - Version history and changelogs

### Branding Assets
- `images/` - Southwest Airlines logos and branding materials

## 🎯 Key Features (v{version})

- ✅ **True Offline Operation** - Zero internet requirements
- ✅ **Local Plotly.js Library** - No CDN dependencies
- ✅ **Interactive Charts** - Zoom, pan, export capabilities
- ✅ **Wheeler's SPC Rules** - Professional statistical process control
- ✅ **Southwest Airlines Branding** - Professional appearance
- ✅ **Comprehensive Testing** - Automated validation included

## 📋 Requirements

- Python 3.7+ (standard library only)
- Modern web browser (Chrome, Edge, Firefox, Safari)
- No admin rights required
- No internet connection required
- Storage: ~15MB total package size

## 🧪 Validation

Run the offline functionality test:
```bash
python test_offline_functionality.py
```

## 📞 Support

**Technical Operations Analytics Team**  
Southwest Airlines  
Internal Use Only

**Version:** {version}  
**Release Date:** {release_date}  
**Package:** {package_name}.zip

---

*This package provides complete offline capability for the Southwest Airlines Tech Ops SPC Dashboard, suitable for air-gapped environments and secure deployments.*
""")
    
    print(f"  ✅ README_PACKAGE.md created")
    
    # Create the ZIP file
    print(f"\n📦 Creating ZIP package...")
    zip_filename = f"{package_name}.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, temp_dir.parent)
                zipf.write(file_path, arc_path)
    
    # Get package statistics
    zip_size = os.path.getsize(zip_filename) / (1024 * 1024)
    file_count = len(list(temp_dir.rglob("*")))
    
    print(f"  ✅ {zip_filename} created ({zip_size:.1f}MB)")
    print(f"  📊 {file_count} files packaged")
    
    # Cleanup temporary directory
    shutil.rmtree(temp_dir)
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 RELEASE PACKAGE CREATED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Package: {zip_filename}")
    print(f"Size: {zip_size:.1f}MB")
    print(f"Files: {file_count}")
    print(f"Version: {version}")
    print(f"Date: {release_date}")
    print("\n📋 Package Contents:")
    print("  ✅ Core application files")
    print("  ✅ Local Plotly.js library (offline capable)")
    print("  ✅ Complete documentation suite")
    print("  ✅ Southwest Airlines branding")
    print("  ✅ Sample data and test files")
    print("  ✅ Release notes and changelogs")
    print("  ✅ Automated testing tools")
    
    print(f"\n🚀 Ready for distribution: {zip_filename}")
    
    return zip_filename

if __name__ == "__main__":
    try:
        package_file = create_release_package()
        print(f"\n✅ Success! Package created: {package_file}")
    except Exception as e:
        print(f"\n❌ Error creating package: {str(e)}")
        import traceback
        traceback.print_exc()