#!/usr/bin/env python
"""
Manually compile translation files using polib since GNU gettext tools are not available
"""
import polib
import os

def compile_po_file(po_file_path):
    """Compile a .po file to .mo file using polib"""
    try:
        # Load the .po file
        po = polib.pofile(po_file_path)
        
        # Get the .mo file path
        mo_file_path = po_file_path.replace('.po', '.mo')
        
        # Save as .mo file
        po.save_as_mofile(mo_file_path)
        
        print(f"Successfully compiled {po_file_path} to {mo_file_path}")
        return True
    except Exception as e:
        print(f"Error compiling {po_file_path}: {str(e)}")
        return False

def main():
    """Main function to compile all translation files"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    locale_dir = os.path.join(base_dir, 'locale')
    
    success_count = 0
    total_count = 0
    
    # Find all .po files in the locale directory
    for root, dirs, files in os.walk(locale_dir):
        for file in files:
            if file.endswith('.po'):
                po_file_path = os.path.join(root, file)
                total_count += 1
                
                if compile_po_file(po_file_path):
                    success_count += 1
    
    print(f"\nCompilation complete: {success_count}/{total_count} files compiled successfully")

if __name__ == "__main__":
    main()
