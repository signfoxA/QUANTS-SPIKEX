#!/usr/bin/env python3
"""
Convert Jupyter notebooks to HTML
"""
import sys
import os
from pathlib import Path

try:
    from nbconvert import HTMLExporter
    import nbformat
except ImportError:
    print("Error: nbconvert is not installed. Please install it with:")
    print("  pip install nbconvert")
    sys.exit(1)

def convert_notebook_to_html(notebook_path, output_path=None):
    """Convert a Jupyter notebook to HTML"""
    notebook_path = Path(notebook_path)
    
    if not notebook_path.exists():
        print(f"Error: Notebook file not found: {notebook_path}")
        return False
    
    if output_path is None:
        output_path = notebook_path.with_suffix('.html')
    else:
        output_path = Path(output_path)
    
    try:
        # Read the notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        
        # Convert to HTML
        # Use HTMLExporter with minimal configuration to avoid template issues
        html_exporter = HTMLExporter(config={
            'HTMLExporter': {
                'template_name': 'basic'
            }
        })
        
        # If that fails, try without template
        try:
            (body, resources) = html_exporter.from_notebook_node(notebook)
        except Exception as e:
            # Fallback: use default exporter without template
            html_exporter = HTMLExporter()
            html_exporter.template_file = None
            (body, resources) = html_exporter.from_notebook_node(notebook)
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(body)
        
        print(f"Successfully converted {notebook_path.name} to {output_path.name}")
        return True
        
    except Exception as e:
        print(f"Error converting {notebook_path.name}: {e}")
        return False

if __name__ == "__main__":
    # Get the examples directory
    script_dir = Path(__file__).parent
    examples_dir = script_dir / "examples"
    
    # Convert both notebooks
    notebooks = [
        examples_dir / "spot_guide.ipynb",
        examples_dir / "future_guide.ipynb"
    ]
    
    success_count = 0
    for notebook in notebooks:
        if convert_notebook_to_html(notebook):
            success_count += 1
    
    if success_count == len(notebooks):
        print(f"\n✓ Successfully converted {success_count} notebook(s)")
        sys.exit(0)
    else:
        print(f"\n✗ Only {success_count} out of {len(notebooks)} notebook(s) converted successfully")
        sys.exit(1)
