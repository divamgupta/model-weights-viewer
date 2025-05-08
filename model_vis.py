
import json
import re
from collections import defaultdict
from safetensors import safe_open
# Define supported file extensions globally
SUPPORTED_FILE_EXTS = ['.safetensors']

def calculate_params(shape):
    """Calculate the number of parameters based on shape"""
    if not shape:
        return 0
    total = 1
    for dim in shape:
        total *= dim
    return total

def parse_state_dict(keys_and_shapes):
    """Parse state dict keys and shapes into a hierarchical structure"""
    # Process the input string to extract keys and shapes
    lines = keys_and_shapes.strip().split('\n')
    parsed_data = {}
    
    for line in lines:
        if '->' in line:
            key, shape_str = line.split('->')
            key = key.strip()
            # Extract shape values from the string
            shape_match = re.search(r'\[(.*?)\]', shape_str)
            if shape_match:
                shape_values = shape_match.group(1).strip()
                if shape_values:
                    # Convert shape values to integers
                    shape = [int(x.strip()) for x in shape_values.split(',')]
                else:
                    shape = []
            else:
                shape = []
        else:
            key = line.strip()
            shape = []
        
        parsed_data[key] = shape
    
    return parsed_data

def build_hierarchy(keys_and_shapes):
    """Build a hierarchical structure from state dict keys"""
    parsed_data = parse_state_dict(keys_and_shapes)
    hierarchy = {}
    
    for key, shape in parsed_data.items():
        parts = key.split('.')
        current = hierarchy
        
        # Navigate through the hierarchy
        for i, part in enumerate(parts):
            if i == len(parts) - 1:  # Last part (leaf node)
                current[part] = {
                    'type': 'parameter',
                    'shape': shape,
                    'params': calculate_params(shape)
                }
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]
    
    return hierarchy

def calculate_total_params(node):
    """Calculate total parameters in a node and its children"""
    if isinstance(node, dict) and 'type' in node and node['type'] == 'parameter':
        return node['params']
    
    total = 0
    for key, value in node.items():
        if isinstance(value, dict):
            total += calculate_total_params(value)
    return total

def format_params(params):
    """Format parameter count as K for thousands and M for millions"""
    if params >= 1_000_000:
        return f"{params / 1_000_000:.2f}M"
    elif params >= 1000:
        return f"{params / 1000:.2f}K"
    else:
        return f"{params}"

def generate_html(hierarchy):
    """Generate HTML visualization of the hierarchy"""
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PyTorch State Dict Visualizer</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                color: #333;
                text-align: center;
            }
            .module {
                border: 1px solid #ddd;
                margin: 10px 0;
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .module-header {
                padding: 10px 15px;
                background-color: #f1f1f1;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-radius: 5px 5px 0 0;
            }
            .module-header:hover {
                background-color: #e9e9e9;
            }
            .module-content {
                padding: 10px 15px;
                display: none;
                border-top: 1px solid #ddd;
            }
            .parameter {
                padding: 5px 15px;
                background-color: #f9f9f9;
                margin: 5px 0;
                border-radius: 3px;
                border-left: 3px solid #4CAF50;
            }
            .toggle-icon {
                margin-right: 10px;
                font-weight: bold;
            }
            .params-info {
                color: #666;
                font-size: 0.9em;
            }
            .shape-info {
                color: #0066cc;
                font-weight: bold;
            }
            .nested {
                margin-left: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div id="visualization">
                CONTENT_PLACEHOLDER
            </div>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Add click handlers to all module headers
                const headers = document.querySelectorAll('.module-header');
                headers.forEach(header => {
                    header.addEventListener('click', function() {
                        // Toggle the visibility of the next sibling (module content)
                        const content = this.nextElementSibling;
                        const isVisible = content.style.display === 'block';
                        content.style.display = isVisible ? 'none' : 'block';
                        
                        // Change the toggle icon
                        const icon = this.querySelector('.toggle-icon');
                        icon.textContent = isVisible ? '▶' : '▼';
                    });
                });
                
                // Expand the top-level module by default
                const topModule = document.querySelector('.module-header');
                if (topModule) {
                    topModule.click();
                }
            });
        </script>
    </body>
    </html>
    """
    
    def render_node(name, node, level=0):
        if isinstance(node, dict) and 'type' in node and node['type'] == 'parameter':
            # Render parameter
            shape_str = f"[{', '.join(map(str, node['shape']))}]" if node['shape'] else "[]"
            params_formatted = format_params(node['params'])
            return f"""
            <div class="parameter">
                <span>{name}</span>
                <span class="shape-info">{shape_str}</span>
                <span class="params-info">({params_formatted} params)</span>
            </div>
            """
        else:
            # Render module
            total_params = calculate_total_params(node)
            params_formatted = format_params(total_params)
            
            content = f"""
            <div class="module{'nested' if level > 0 else ''}">
                <div class="module-header">
                    <span><span class="toggle-icon">▶</span>{name}</span>
                    <span class="params-info">{params_formatted} params</span>
                </div>
                <div class="module-content">
            """
            
            # Sort keys to have a consistent order
            for key in sorted(node.keys()):
                content += render_node(key, node[key], level + 1)
            
            content += """
                </div>
            </div>
            """
            return content
    
    # Generate HTML content for the hierarchy
    html_content = ""
    for key in sorted(hierarchy.keys()):
        html_content += render_node(key, hierarchy[key])
    
    # Replace placeholder with actual content
    html = html_template.replace("CONTENT_PLACEHOLDER", html_content)
    return html


def model_file_vis(safetensors_file):
    keys_and_shapes = ""
    
    with safe_open(safetensors_file, framework="pt", device=0) as f:
        for k in f.keys():
            keys_and_shapes +=  k + " -> " + str(f.get_slice(k).get_shape()) + "\n"
    
    # Build hierarchy and generate HTML
    hierarchy = build_hierarchy(keys_and_shapes)
    html = generate_html(hierarchy)
    return html 
