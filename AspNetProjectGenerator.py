import anthropic
import os
import re
from pathlib import Path

class AspNetProjectGenerator:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate_project(self, project_type, project_name, output_dir):
        """Generate ASP.NET project files using Claude API"""
        
        include_views = "mvc" in project_type.lower() or "web app" in project_type.lower()
        
        view_files = """
7. Views/_ViewStart.cshtml
8. Views/_ViewImports.cshtml
9. Views/Shared/_Layout.cshtml
10. Views/Home/Index.cshtml
11. Views/Home/Privacy.cshtml
12. wwwroot/css/site.css
13. wwwroot/js/site.js""" if include_views else ""
        
        controller_file = "HomeController.cs" if include_views else "WeatherForecastController.cs"
        model_file = "ErrorViewModel.cs" if include_views else "WeatherForecast.cs"
        
        prompt = f"""Generate a {project_type} ASP.NET Core project named '{project_name}'.

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
5. Controllers/{controller_file}
6. Models/{model_file}{view_files}

Make it production-ready with proper namespaces and .NET 8 patterns."""

        system_prompt = """You are an expert ASP.NET Core developer specializing in project scaffolding. 
When generating files:
- Create complete, working code with no placeholders
- Use proper .NET 8 conventions and modern C# features
- Include all necessary using statements
- Follow RESTful API best practices for Web APIs
- For MVC projects, generate complete Razor views with proper layout and styling
- Include proper dependency injection setup
- Add comprehensive error handling
- Use async/await patterns correctly
- Generate production-ready configuration files
- For Razor views, use Bootstrap 5 for styling and include proper tag helpers"""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Parse and save files
        files = self._parse_files(response_text)
        self._save_files(files, output_dir)
        
        return files
    
    def generate_views_for_entity(self, entity_name, project_name, output_dir):
        """Generate complete CRUD views for an entity"""
        
        prompt = f"""Generate complete CRUD Razor views for an entity named '{entity_name}' in ASP.NET Core MVC.

For each file, use this format:
FILE: <filename>
```
<file content>
```

Generate these view files:
1. Views/{entity_name}/Index.cshtml (list all items with search and pagination)
2. Views/{entity_name}/Details.cshtml (show single item details)
3. Views/{entity_name}/Create.cshtml (create form with validation)
4. Views/{entity_name}/Edit.cshtml (edit form with validation)
5. Views/{entity_name}/Delete.cshtml (delete confirmation)

Also generate:
6. Controllers/{entity_name}Controller.cs (full CRUD controller)
7. Models/{entity_name}.cs (model with data annotations)
8. Models/{entity_name}ViewModel.cs (view model for forms)

Use Bootstrap 5, proper tag helpers, validation, and modern Razor syntax."""

        system_prompt = """You are an expert ASP.NET Core MVC developer. Generate complete, production-ready Razor views with:
- Bootstrap 5 styling and components
- Proper model binding and tag helpers
- Client and server-side validation
- Responsive design
- Accessibility features (ARIA labels, proper form structure)
- CSRF protection
- Proper error handling and user feedback
- Clean, semantic HTML
- Modern C# and Razor syntax"""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Parse and save files
        files = self._parse_files(response_text)
        self._save_files(files, output_dir)
        
        return files
    
    def generate_single_file(self, file_type, file_name, specifications):
        """Generate a single file based on specifications"""
        
        prompt = f"""Generate a {file_type} file named '{file_name}' for ASP.NET Core.

Specifications:
{specifications}

Provide the complete file content with proper namespaces and using statements."""

        system_prompt = """You are an expert ASP.NET Core developer. Generate clean, production-ready code following best practices:
- Use .NET 8 patterns and conventions
- Include proper error handling
- Use async/await correctly
- Follow SOLID principles
- Include necessary using statements
- Use meaningful variable names"""

        message = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return message.content[0].text
    
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
            
            print(f"✓ Generated: {file_path}")

def main():
    """Main interactive menu"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ Please set ANTHROPIC_API_KEY environment variable")
        return
    
    generator = AspNetProjectGenerator(api_key)
    
    print("\n" + "="*50)
    print("ASP.NET Project Generator using Claude API")
    print("="*50)
    print("\nChoose an option:")
    print("1. Generate Web API Project")
    print("2. Generate MVC Web Application")
    print("3. Generate CRUD Views for Entity")
    print("4. Generate Single File (Controller/Model/View)")
    print("5. Exit")
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        print("\n--- Web API Project ---")
        project_name = input("Project name (default: MyApiProject): ").strip() or "MyApiProject"
        output_dir = input("Output directory (default: ./GeneratedApiProject): ").strip() or "./GeneratedApiProject"
        
        print("\n🔄 Generating Web API project...")
        files = generator.generate_project("Web API", project_name, output_dir)
        
        print(f"\n✅ Generated {len(files)} files in {output_dir}")
        print("\nTo run the project:")
        print(f"  cd {output_dir}")
        print("  dotnet restore")
        print("  dotnet run")
        
    elif choice == "2":
        print("\n--- MVC Web Application ---")
        project_name = input("Project name (default: MyMvcProject): ").strip() or "MyMvcProject"
        output_dir = input("Output directory (default: ./GeneratedMvcProject): ").strip() or "./GeneratedMvcProject"
        
        print("\n🔄 Generating MVC project...")
        files = generator.generate_project("MVC Web Application", project_name, output_dir)
        
        print(f"\n✅ Generated {len(files)} files in {output_dir}")
        print("\nTo run the project:")
        print(f"  cd {output_dir}")
        print("  dotnet restore")
        print("  dotnet run")
        
    elif choice == "3":
        print("\n--- CRUD Views Generator ---")
        entity_name = input("Entity name (e.g., Product, Customer): ").strip()
        
        if not entity_name:
            print("❌ Entity name is required!")
            return
        
        project_name = input("Project name (default: MyProject): ").strip() or "MyProject"
        output_dir = input("Output directory (default: ./GeneratedViews): ").strip() or "./GeneratedViews"
        
        print(f"\n🔄 Generating CRUD views for {entity_name}...")
        files = generator.generate_views_for_entity(entity_name, project_name, output_dir)
        
        print(f"\n✅ Generated {len(files)} files in {output_dir}")
        print("\n📋 Copy these files to your existing MVC project:")
        for file_path in files.keys():
            print(f"  - {file_path}")
        
    elif choice == "4":
        print("\n--- Single File Generator ---")
        print("File types: Controller, Model, View, Service, Repository")
        file_type = input("File type: ").strip()
        file_name = input("File name: ").strip()
        specifications = input("Specifications (describe what you want): ").strip()
        
        if not all([file_type, file_name, specifications]):
            print("❌ All fields are required!")
            return
        
        print(f"\n🔄 Generating {file_type}...")
        content = generator.generate_single_file(file_type, file_name, specifications)
        
        print("\n" + "="*50)
        print(content)
        print("="*50)
        
        save = input("\nSave to file? (y/n): ").strip().lower()
        if save == 'y':
            output_file = input("Output file path: ").strip()
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Saved to {output_file}")
    
    elif choice == "5":
        print("\n👋 Goodbye!")
        
    else:
        print("\n❌ Invalid choice!")

if __name__ == "__main__":
    main()