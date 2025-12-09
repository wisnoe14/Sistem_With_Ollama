"""
Script untuk menambahkan section markers ke gpt_service.py
untuk memudahkan navigasi tanpa harus restruktur complete
"""

import re

def add_section_markers():
    """Add clear section markers to existing file"""
    
    # Read original file
    with open('gpt_service.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Define markers to insert
    markers = {
        # After imports, before first constant
        'START_DATA': '\n# ' + '='*60 + '\n# 📊 DATA & CONSTANTS SECTION\n# ' + '='*60 + '\n\n',
        
        # Before TELECOLLECTION data
        'TELECOLLECTION_DATA': '\n# ' + '-'*60 + '\n# 📞 TELECOLLECTION DATA\n# ' + '-'*60 + '\n',
        
        # Before WINBACK data  
        'WINBACK_DATA': '\n# ' + '-'*60 + '\n# 🔄 WINBACK DATA\n# ' + '-'*60 + '\n',
        
        # Before functions section
        'START_FUNCTIONS': '\n# ' + '='*60 + '\n# 🔧 FUNCTIONS SECTION\n# ' + '='*60 + '\n\n',
        
        # Before telecollection functions
        'TELECOLLECTION_FUNCS': '\n# ' + '-'*60 + '\n# 📞 TELECOLLECTION FUNCTIONS\n# ' + '-'*60 + '\n',
        
        # Before winback functions
        'WINBACK_FUNCS': '\n# ' + '-'*60 + '\n# 🔄 WINBACK FUNCTIONS\n# ' + '-'*60 + '\n',
        
        # Before shared functions
        'SHARED_FUNCS': '\n# ' + '-'*60 + '\n# 🔧 SHARED/UTILITY FUNCTIONS\n# ' + '-'*60 + '\n',
    }
    
    new_lines = []
    
    for i, line in enumerate(lines):
        # Detect where to insert markers
        
        # Insert TELECOLLECTION_DATA marker before TELECOLLECTION_GOALS
        if 'TELECOLLECTION_GOALS' in line and i > 0:
            if markers['TELECOLLECTION_DATA'] not in new_lines:
                new_lines.append(markers['TELECOLLECTION_DATA'])
        
        # Insert WINBACK_DATA marker before WINBACK_QUESTIONS
        if 'WINBACK_QUESTIONS' in line and i > 0:
            if markers['WINBACK_DATA'] not in new_lines:
                new_lines.append(markers['WINBACK_DATA'])
        
        # Insert TELECOLLECTION_FUNCS marker before first telecollection function
        if line.startswith('def ') and 'telecollection' in line.lower():
            if markers['TELECOLLECTION_FUNCS'] not in new_lines:
                new_lines.append(markers['TELECOLLECTION_FUNCS'])
        
        # Insert WINBACK_FUNCS marker before first winback function
        if line.startswith('def ') and 'winback' in line.lower():
            if markers['WINBACK_FUNCS'] not in new_lines:
                new_lines.append(markers['WINBACK_FUNCS'])
        
        new_lines.append(line)
    
    # Write back with markers
    with open('gpt_service_MARKED.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ Section markers added to gpt_service_MARKED.py")
    print("\n📋 Sections created:")
    print("   📞 TELECOLLECTION DATA")
    print("   🔄 WINBACK DATA")
    print("   📞 TELECOLLECTION FUNCTIONS")
    print("   🔄 WINBACK FUNCTIONS")
    print("   🔧 SHARED/UTILITY FUNCTIONS")

if __name__ == '__main__':
    print("🚀 Adding section markers to gpt_service.py...")
    add_section_markers()
