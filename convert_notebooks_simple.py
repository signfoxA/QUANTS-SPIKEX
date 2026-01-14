#!/usr/bin/env python3
"""
Simple notebook to HTML converter that works around template issues
"""
import sys
import json
import html
from pathlib import Path

def notebook_to_html(notebook_path, output_path=None):
    """Convert Jupyter notebook to HTML without using nbconvert templates"""
    notebook_path = Path(notebook_path)
    
    if not notebook_path.exists():
        print(f"Error: Notebook file not found: {notebook_path}")
        return False
    
    if output_path is None:
        output_path = notebook_path.with_suffix('.html')
    else:
        output_path = Path(output_path)
    
    try:
        # Read notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        # Generate HTML
        html_content = generate_html(notebook)
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ Successfully converted {notebook_path.name} to {output_path.name}")
        return True
        
    except Exception as e:
        print(f"Error converting {notebook_path.name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_html(notebook):
    """Generate HTML from notebook JSON"""
    html_parts = []
    
    # HTML header
    html_parts.append("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Notebook</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
        }
        .cell {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }
        .markdown-cell {
            background-color: #f9f9f9;
        }
        .code-cell {
            background-color: #f5f5f5;
        }
        pre {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
        code {
            font-family: "Monaco", "Menlo", "Ubuntu Mono", monospace;
            font-size: 13px;
        }
        h1, h2, h3 {
            color: #333;
        }
        .output {
            margin-top: 10px;
            padding: 10px;
            background-color: #fff;
            border-left: 3px solid #4CAF50;
        }
    </style>
</head>
<body>
""")
    
    # Process cells
    for cell in notebook.get('cells', []):
        cell_type = cell.get('cell_type', '')
        source = ''.join(cell.get('source', []))
        
        if cell_type == 'markdown':
            html_parts.append('<div class="cell markdown-cell">')
            # Simple markdown to HTML conversion
            html_source = html.escape(source)
            # Convert headers
            html_source = html_source.replace('\n# ', '\n<h1>').replace('\n## ', '\n<h2>').replace('\n### ', '\n<h3>')
            html_source = html_source.replace('\n', '<br>\n')
            html_parts.append(html_source)
            html_parts.append('</div>')
        
        elif cell_type == 'code':
            html_parts.append('<div class="cell code-cell">')
            html_parts.append('<pre><code>')
            html_parts.append(html.escape(source))
            html_parts.append('</code></pre>')
            
            # Add outputs if any
            outputs = cell.get('outputs', [])
            if outputs:
                html_parts.append('<div class="output">')
                html_parts.append('<strong>Output:</strong><br>')
                for output in outputs:
                    output_type = output.get('output_type', '')
                    if output_type == 'stream':
                        text = ''.join(output.get('text', []))
                        html_parts.append('<pre>' + html.escape(text) + '</pre>')
                    elif output_type == 'execute_result' or output_type == 'display_data':
                        data = output.get('data', {})
                        if 'text/plain' in data:
                            html_parts.append('<pre>' + html.escape(''.join(data['text/plain'])) + '</pre>')
                html_parts.append('</div>')
            
            html_parts.append('</div>')
    
    # HTML footer
    html_parts.append("""
</body>
</html>
""")
    
    return '\n'.join(html_parts)

if __name__ == "__main__":
    script_dir = Path(__file__).parent
    examples_dir = script_dir / "examples"
    
    notebooks = [
        examples_dir / "spot_guide.ipynb",
        examples_dir / "future_guide.ipynb"
    ]
    
    success_count = 0
    for notebook in notebooks:
        if notebook_to_html(notebook):
            success_count += 1
    
    if success_count == len(notebooks):
        print(f"\n✓ Successfully converted {success_count} notebook(s)")
        sys.exit(0)
    else:
        print(f"\n✗ Only {success_count} out of {len(notebooks)} notebook(s) converted successfully")
        sys.exit(1)
