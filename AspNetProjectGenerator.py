import anthropic
import os
import re
from pathlib import Path

class AspNetProjectGenerator:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate_project(self, project_type, project_name, output_dir):
        """Generate ASP.NET project files using Claude API"""
        
        prompt = f"""Generate a complete {project_type} ASP.NET Core project named '{project_name}' for .NET 8.

For each file, use this exact format:
FILE: <relative/path/to/file>
```
<file content>
```

Generate these files:
1. {project_name}.csproj
2. Program.cs
3. appsettings.json
4. appsettings.Development.json
5. Controllers/WeatherForecastController.cs
6. Models/WeatherForecast.cs
7. Properties/launchSettings.json

Use modern .NET 8 patterns with minimal APIs where appropriate."""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Parse and save files
        files = self._parse_files(response_text)
        self._save_files(files, output_dir)
        
        return files
    
    def _parse_files(self, response):
        """Parse generated files from Claude's response"""
        files = {}
        lines = response.split('\n')
        
        current_file = None
        current_content = []
        in_code_block = False
        
        for line in lines:
            if line.startswith('FILE:'):
                # Save previous file
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content).strip()
                
                current_file = line[5:].strip()
                current_content = []
                in_code_block = False
                
            elif line.startswith('```') and current_file:
                in_code_block = not in_code_block
                
            elif in_code_block and current_file:
                current_content.append(line)
        
        # Save last file
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content).strip()
        
        return files
    
    def _save_files(self, files, output_dir):
        """Save generated files to disk"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for file_path, content in files.items():
            full_path = output_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Generated: {file_path}")

# Usage
if __name__ == "__main__":
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("Please set ANTHROPIC_API_KEY environment variable")
        exit(1)
    
    generator = AspNetProjectGenerator(api_key)
    
    files = generator.generate_project(
        project_type="Web API",
        project_name="MyApiProject",
        output_dir="./GeneratedProject"
    )
    
    print(f"\n✓ Generated {len(files)} files")
    print("\nTo run the project:")
    print("cd GeneratedProject")
    print("dotnet restore")
    print("dotnet run")