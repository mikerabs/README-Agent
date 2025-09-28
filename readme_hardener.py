#!/usr/bin/env python3
"""README & Script Hardener CLI.

A tool to enhance Python scripts and repositories with better documentation,
type hints, and comprehensive README files.

This tool provides two main modes:
1. Single-file mode: Enhances a single Python file with docstrings, type hints, and README
2. Repo mode: Analyzes repository structure and generates comprehensive README sections
"""

import argparse
import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

try:
    import openai
    from dotenv import load_dotenv
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ScriptHardener:
    """Handles enhancement of individual Python scripts."""
    
    def __init__(self, script_path: str) -> None:
        """Initialize the script hardener.
        
        Args:
            script_path: Path to the Python script to enhance
        """
        self.script_path = Path(script_path)
        self.content = ""
        self.tree: Optional[ast.AST] = None
        
    def analyze_script(self) -> Dict[str, any]:
        """Analyze the Python script to extract information.
        
        Returns:
            Dictionary containing script analysis results
        """
        if not self.script_path.exists():
            raise FileNotFoundError(f"Script not found: {self.script_path}")
            
        with open(self.script_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
            
        try:
            self.tree = ast.parse(self.content)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax in {self.script_path}: {e}")
            
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'has_main': False,
            'has_argparse': False,
            'missing_docstrings': [],
            'missing_type_hints': []
        }
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                analysis['functions'].append({
                    'name': node.name,
                    'line': node.lineno,
                    'has_docstring': ast.get_docstring(node) is not None,
                    'has_type_hints': self._has_type_hints(node)
                })
                if node.name == 'main':
                    analysis['has_main'] = True
                    
            elif isinstance(node, ast.ClassDef):
                analysis['classes'].append({
                    'name': node.name,
                    'line': node.lineno,
                    'has_docstring': ast.get_docstring(node) is not None
                })
                
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    analysis['imports'].append(alias.name)
                    if alias.name == 'argparse':
                        analysis['has_argparse'] = True
                        
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        full_name = f"{node.module}.{alias.name}"
                        analysis['imports'].append(full_name)
                        if node.module == 'argparse':
                            analysis['has_argparse'] = True
        
        return analysis
    
    def _has_type_hints(self, node: ast.FunctionDef) -> bool:
        """Check if a function has type hints.
        
        Args:
            node: AST function definition node
            
        Returns:
            True if function has type hints
        """
        has_hints = bool(node.returns)
        for arg in node.args.args:
            if arg.annotation:
                has_hints = True
                break
        return has_hints
    
    def enhance_script(self, output_path: Optional[str] = None) -> str:
        """Enhance the script with docstrings, type hints, and argparse.
        
        Args:
            output_path: Optional output path, defaults to input path
            
        Returns:
            Path to the enhanced script
        """
        analysis = self.analyze_script()
        enhanced_content = self._add_missing_components(analysis)
        
        if output_path is None:
            output_path = str(self.script_path)
        
        # Create backup
        backup_path = f"{self.script_path}.backup"
        if not Path(backup_path).exists():
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(self.content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
            
        return output_path
    
    def _add_missing_components(self, analysis: Dict[str, any]) -> str:
        """Add missing components to the script.
        
        Args:
            analysis: Script analysis results
            
        Returns:
            Enhanced script content
        """
        lines = self.content.split('\n')
        
        # Add common imports if missing
        import_additions = []
        if not analysis['has_argparse']:
            import_additions.append('import argparse')
        
        if 'typing' not in ' '.join(analysis['imports']):
            import_additions.append('from typing import Dict, List, Optional, Union')
        
        if import_additions:
            # Find where to insert imports
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('"""') or line.strip().startswith("'''"):
                    # Skip docstring
                    quote_type = '"""' if line.strip().startswith('"""') else "'''"
                    for j in range(i + 1, len(lines)):
                        if quote_type in lines[j]:
                            insert_pos = j + 1
                            break
                    break
                elif line.strip() and not line.strip().startswith('#'):
                    insert_pos = i
                    break
            
            for imp in reversed(import_additions):
                lines.insert(insert_pos, imp)
        
        # Add module docstring if missing
        if not lines[0].strip().startswith('"""') and not lines[0].strip().startswith("'''"):
            module_docstring = f'"""Enhanced script: {self.script_path.name}.\n\nThis script has been enhanced with type hints and documentation.\n"""\n'
            # Find position after imports
            import_end = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    import_end = i + 1
                elif line.strip() and not line.strip().startswith('#') and not (line.strip().startswith('import ') or line.strip().startswith('from ')):
                    break
            
            lines.insert(import_end, module_docstring)
        
        return '\n'.join(lines)
    
    def generate_readme(self, output_dir: str = ".") -> str:
        """Generate a minimal README for the script.
        
        Args:
            output_dir: Directory to write README
            
        Returns:
            Path to generated README
        """
        analysis = self.analyze_script()
        readme_path = Path(output_dir) / f"README_{self.script_path.stem}.md"
        
        readme_content = f"""# {self.script_path.name}

## Description
Enhanced Python script with improved documentation and type hints.

## Usage
```bash
python {self.script_path.name} --help
```

## Functions
"""
        
        for func in analysis['functions']:
            readme_content += f"- `{func['name']}()` (line {func['line']})\n"
        
        if analysis['classes']:
            readme_content += "\n## Classes\n"
            for cls in analysis['classes']:
                readme_content += f"- `{cls['name']}` (line {cls['line']})\n"
        
        readme_content += f"""
## Dependencies
```python
{chr(10).join(analysis['imports'])}
```

<!-- README-HARDENER-MARKER: {self.script_path.name} -->
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
            
        return str(readme_path)


class RepoHardener:
    """Handles repository-wide README generation and enhancement."""
    
    def __init__(self, repo_path: str = ".") -> None:
        """Initialize the repository hardener.
        
        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = Path(repo_path)
        self.detected_files: Dict[str, List[str]] = {}
        
        # Load environment variables
        if OPENAI_AVAILABLE:
            load_dotenv()
            self.openai_client = None
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
        
    def detect_project_files(self) -> Dict[str, List[str]]:
        """Detect relevant project files in the repository.
        
        Returns:
            Dictionary mapping file types to found files
        """
        patterns = {
            'dockerfile': ['Dockerfile*', 'dockerfile*'],
            'docker_compose': ['docker-compose*.yml', 'docker-compose*.yaml', 'compose*.yml', 'compose*.yaml'],
            'python_deps': ['requirements*.txt', 'pyproject.toml', 'setup.py', 'Pipfile', 'poetry.lock'],
            'makefile': ['Makefile', 'makefile'],
            'env_files': ['.env.example', '.env.template', '.env.sample'],
            'python_scripts': ['*.py'],
            'config_files': ['*.yml', '*.yaml', '*.toml', '*.json', '*.ini', '*.cfg']
        }
        
        detected = {key: [] for key in patterns.keys()}
        
        for file_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = list(self.repo_path.glob(pattern))
                matches.extend(list(self.repo_path.glob(f"**/{pattern}")))
                detected[file_type].extend([str(f.relative_to(self.repo_path)) for f in matches])
        
        # Remove duplicates
        for key in detected:
            detected[key] = list(set(detected[key]))
            
        self.detected_files = detected
        return detected
    
    def analyze_makefile(self, makefile_path: str) -> List[str]:
        """Analyze Makefile to extract targets.
        
        Args:
            makefile_path: Path to Makefile
            
        Returns:
            List of make targets
        """
        targets = []
        try:
            with open(self.repo_path / makefile_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and ':' in line and not line.startswith('#') and not line.startswith('\t'):
                        target = line.split(':')[0].strip()
                        if target and not target.startswith('.'):
                            targets.append(target)
        except Exception:
            pass
        return targets
    
    def analyze_env_file(self, env_path: str) -> List[Tuple[str, str]]:
        """Analyze environment file to extract variables.
        
        Args:
            env_path: Path to environment file
            
        Returns:
            List of (variable, description) tuples
        """
        variables = []
        try:
            with open(self.repo_path / env_path, 'r', encoding='utf-8') as f:
                current_comment = ""
                for line in f:
                    line = line.strip()
                    if line.startswith('#'):
                        current_comment = line[1:].strip()
                    elif '=' in line and not line.startswith('#'):
                        var_name = line.split('=')[0].strip()
                        variables.append((var_name, current_comment))
                        current_comment = ""
        except Exception:
            pass
        return variables
    
    def generate_readme(self, output_path: str = "README.md", notes: Optional[str] = None) -> str:
        """Generate comprehensive README for the repository.
        
        Args:
            output_path: Path to output README
            notes: Additional notes to include
            
        Returns:
            Path to generated README
        """
        detected = self.detect_project_files()
        readme_content = self._build_readme_content(detected, notes)
        
        output_file = self.repo_path / output_path
        
        # Handle existing README
        if output_file.exists():
            readme_content = self._merge_with_existing(str(output_file), readme_content)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
            
        return str(output_file)
    
    def generate_readme_with_openai(self, output_path: str = "README.md", notes: Optional[str] = None) -> str:
        """Generate comprehensive README for the repository using OpenAI.
        
        Args:
            output_path: Path to output README
            notes: Additional notes to include
            
        Returns:
            Path to generated README
            
        Raises:
            RuntimeError: If OpenAI is not available or API key is not set
        """
        if not OPENAI_AVAILABLE:
            raise RuntimeError("OpenAI integration requires 'openai' and 'python-dotenv' packages. Install with: pip install openai python-dotenv")
        
        if not self.openai_client:
            raise RuntimeError("OpenAI API key not found. Please set OPENAI_API_KEY in your environment or .env file")
        
        # Analyze repository structure
        detected = self.detect_project_files()
        project_name = os.path.basename(os.path.abspath(self.repo_path))
        
        # Gather context about the project
        context_info = self._gather_project_context(detected)
        
        # Create prompt for OpenAI
        prompt = self._create_readme_prompt(project_name, context_info, notes)
        
        try:
            # Generate README using OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert technical writer specializing in creating comprehensive README files for software projects."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            ai_generated_content = response.choices[0].message.content
            
            # Handle existing README
            output_file = self.repo_path / output_path
            if output_file.exists():
                ai_generated_content = self._merge_with_existing(str(output_file), ai_generated_content)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(ai_generated_content)
                
            return str(output_file)
            
        except Exception as e:
            raise RuntimeError(f"Error generating README with OpenAI: {e}")
    
    def _gather_project_context(self, detected: Dict[str, List[str]]) -> str:
        """Gather context information about the project for OpenAI prompt.
        
        Args:
            detected: Detected project files
            
        Returns:
            Context information as a string
        """
        context_parts = []
        
        # Python files analysis
        if detected['python_scripts']:
            context_parts.append(f"Python scripts: {', '.join(detected['python_scripts'])}")
            
            # Try to read main script for context
            main_scripts = [s for s in detected['python_scripts'] if 'main' in s.lower() or s == 'app.py' or s == 'run.py']
            if not main_scripts and detected['python_scripts']:
                main_scripts = [detected['python_scripts'][0]]  # Use first script as fallback
                
            for script in main_scripts[:1]:  # Only analyze one main script
                try:
                    script_path = self.repo_path / script
                    if script_path.exists():
                        with open(script_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Extract docstrings and function/class names
                            tree = ast.parse(content)
                            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                            if functions:
                                context_parts.append(f"Main functions: {', '.join(functions[:5])}")  # Limit to 5
                            if classes:
                                context_parts.append(f"Main classes: {', '.join(classes[:3])}")  # Limit to 3
                except Exception:
                    pass  # Ignore parsing errors
        
        # Dependencies
        if detected['python_deps']:
            context_parts.append(f"Dependency files: {', '.join(detected['python_deps'])}")
            
            # Read requirements.txt for specific dependencies
            for dep_file in detected['python_deps']:
                if 'requirements' in dep_file:
                    try:
                        req_path = self.repo_path / dep_file
                        if req_path.exists():
                            with open(req_path, 'r', encoding='utf-8') as f:
                                deps = [line.strip().split('>=')[0].split('==')[0] for line in f 
                                       if line.strip() and not line.strip().startswith('#')]
                                if deps:
                                    context_parts.append(f"Key dependencies: {', '.join(deps[:8])}")  # Limit to 8
                    except Exception:
                        pass
        
        # Docker setup
        if detected['dockerfile'] or detected['docker_compose']:
            context_parts.append("Project uses Docker for containerization")
        
        # Make targets
        if detected['makefile']:
            makefile_path = self.repo_path / detected['makefile'][0]
            try:
                targets = self.analyze_makefile(detected['makefile'][0])
                if targets:
                    context_parts.append(f"Available make targets: {', '.join(targets[:6])}")
            except Exception:
                pass
        
        # Environment variables
        if detected['env_files']:
            try:
                env_vars = self.analyze_env_file(detected['env_files'][0])
                if env_vars:
                    var_names = [var[0] for var in env_vars]
                    context_parts.append(f"Environment variables: {', '.join(var_names[:5])}")
            except Exception:
                pass
        
        return "; ".join(context_parts)
    
    def _create_readme_prompt(self, project_name: str, context_info: str, notes: Optional[str]) -> str:
        """Create a prompt for OpenAI to generate README content.
        
        Args:
            project_name: Name of the project
            context_info: Context information about the project
            notes: Additional notes to include
            
        Returns:
            Formatted prompt for OpenAI
        """
        prompt = f"""Create a comprehensive README.md file for a project named "{project_name}".

Project Context:
{context_info}

Please generate a well-structured README that includes:
1. A clear project title and description
2. Installation instructions (based on the detected dependencies)
3. Usage examples
4. Configuration/Environment setup (if applicable)
5. Development setup instructions
6. Contributing guidelines (brief)
7. License section (placeholder)

Make the README professional, clear, and easy to follow. Use proper Markdown formatting.
Focus on practical information that would help users understand and use the project.
"""
        
        if notes:
            prompt += f"\n\nAdditional context/notes to incorporate:\n{notes}"
        
        prompt += "\n\nGenerate only the README content, no extra commentary."
        
        return prompt
    
    def _build_readme_content(self, detected: Dict[str, List[str]], notes: Optional[str]) -> str:
        """Build README content based on detected files.
        
        Args:
            detected: Detected project files
            notes: Additional notes
            
        Returns:
            Generated README content
        """
        project_name = os.path.basename(os.path.abspath(self.repo_path))
        content = f"# {project_name}\n\n"
        
        if notes:
            content += f"{notes}\n\n"
        
        # Installation section
        content += "## Installation\n\n"
        
        if detected['python_deps']:
            content += "### Python Dependencies\n"
            for dep_file in detected['python_deps']:
                if 'requirements' in dep_file:
                    content += f"```bash\npip install -r {dep_file}\n```\n\n"
                elif dep_file == 'pyproject.toml':
                    content += "```bash\npip install -e .\n```\n\n"
                elif dep_file == 'setup.py':
                    content += "```bash\npip install -e .\n```\n\n"
        
        # Running section
        content += "## Running the Application\n\n"
        
        if detected['python_scripts']:
            content += "### Local Development\n"
            main_script = None
            for script in detected['python_scripts']:
                if 'main' in script.lower() or script == 'app.py':
                    main_script = script
                    break
            
            if main_script:
                content += f"```bash\npython {main_script}\n```\n\n"
            else:
                content += "```bash\n# Run your main Python script\npython <script_name>.py\n```\n\n"
        
        # Docker section
        if detected['dockerfile']:
            content += "### Docker\n"
            dockerfile = detected['dockerfile'][0]
            content += f"```bash\n# Build the image\ndocker build -t {project_name.lower()} .\n\n"
            content += f"# Run the container\ndocker run -p 8000:8000 {project_name.lower()}\n```\n\n"
        
        # Docker Compose section
        if detected['docker_compose']:
            content += "### Docker Compose\n"
            compose_file = detected['docker_compose'][0]
            content += f"```bash\n# Start services\ndocker-compose -f {compose_file} up -d\n\n"
            content += f"# Stop services\ndocker-compose -f {compose_file} down\n```\n\n"
        
        # Environment Variables section
        env_vars = []
        for env_file in detected['env_files']:
            env_vars.extend(self.analyze_env_file(env_file))
        
        if env_vars:
            content += "## Environment Variables\n\n"
            content += "| Variable | Description |\n|----------|-------------|\n"
            for var, desc in env_vars:
                content += f"| `{var}` | {desc or 'No description'} |\n"
            content += "\n"
        
        # Make targets section
        make_targets = []
        for makefile in detected['makefile']:
            make_targets.extend(self.analyze_makefile(makefile))
        
        if make_targets:
            content += "## Make Targets\n\n"
            for target in set(make_targets):
                content += f"- `make {target}`\n"
            content += "\n"
        
        # Services section (from docker-compose)
        if detected['docker_compose']:
            content += "## Services\n\n"
            content += "This project uses Docker Compose with the following services:\n\n"
            # Note: Detailed service analysis would require parsing YAML
            content += f"See `{detected['docker_compose'][0]}` for service configuration.\n\n"
        
        content += "<!-- README-HARDENER-MARKER: REPO -->\n"
        return content
    
    def _merge_with_existing(self, existing_path: str, new_content: str) -> str:
        """Merge new README content with existing README.
        
        Args:
            existing_path: Path to existing README
            new_content: New README content to merge
            
        Returns:
            Merged README content
        """
        try:
            with open(existing_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Look for marker
            marker = "<!-- README-HARDENER-MARKER: REPO -->"
            if marker in existing_content:
                # Replace everything after the marker
                parts = existing_content.split(marker)
                return new_content
            else:
                # Append new content
                return f"{existing_content}\n\n{new_content}"
        except Exception:
            return new_content


class READMEHardenerCLI:
    """Main CLI application for README & Script Hardener."""
    
    def __init__(self) -> None:
        """Initialize the CLI application."""
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser.
        
        Returns:
            Configured ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description="README & Script Hardener - Enhance Python scripts and repositories",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Enhance a single Python script
  %(prog)s --script my_script.py
  
  # Generate README for entire repository
  %(prog)s --repo
  
  # Generate README using OpenAI
  %(prog)s --repo --openai
  
  # Specify output location
  %(prog)s --repo --out README_new.md
  
  # Add custom notes
  %(prog)s --repo --notes "This is a special project"
            """
        )
        
        # Mode selection
        mode_group = parser.add_mutually_exclusive_group(required=True)
        mode_group.add_argument(
            "--script",
            metavar="FILE",
            help="Single-file mode: enhance a Python script with docstrings and type hints"
        )
        mode_group.add_argument(
            "--repo",
            action="store_true",
            help="Repository mode: generate comprehensive README for the repository"
        )
        
        # Output options
        parser.add_argument(
            "--out",
            metavar="PATH",
            help="Output file path (default: input file for --script, README.md for --repo)"
        )
        
        # Notes options
        parser.add_argument(
            "--notes",
            metavar="TEXT",
            help="Additional notes to include in README"
        )
        parser.add_argument(
            "--notes-file",
            metavar="FILE",
            help="File containing additional notes to include in README"
        )
        
        # Inclusion options
        parser.add_argument(
            "--include",
            metavar="PATTERNS",
            help="Comma-separated patterns of files to include in analysis"
        )
        
        # Verification
        parser.add_argument(
            "--verify",
            action="store_true",
            help="Run black/ruff verification and show --help output"
        )
        
        # OpenAI integration
        parser.add_argument(
            "--openai",
            action="store_true",
            help="Use OpenAI API to generate README content (requires OPENAI_API_KEY)"
        )
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI application.
        
        Args:
            args: Command line arguments (uses sys.argv if None)
            
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            parsed_args = self.parser.parse_args(args)
            
            # Load notes from file if specified
            notes = parsed_args.notes
            if parsed_args.notes_file:
                try:
                    with open(parsed_args.notes_file, 'r', encoding='utf-8') as f:
                        file_notes = f.read().strip()
                    notes = f"{notes}\n\n{file_notes}" if notes else file_notes
                except Exception as e:
                    print(f"Warning: Could not read notes file: {e}")
            
            if parsed_args.script:
                return self._handle_script_mode(parsed_args)
            elif parsed_args.repo:
                return self._handle_repo_mode(parsed_args, notes)
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        
        return 0
    
    def _handle_script_mode(self, args: argparse.Namespace) -> int:
        """Handle single-file script mode.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Exit code
        """
        print(f"Enhancing script: {args.script}")
        
        hardener = ScriptHardener(args.script)
        
        # Analyze script first
        try:
            analysis = hardener.analyze_script()
            print(f"Found {len(analysis['functions'])} functions, {len(analysis['classes'])} classes")
        except Exception as e:
            print(f"Error analyzing script: {e}", file=sys.stderr)
            return 1
        
        # Enhance script
        try:
            output_path = hardener.enhance_script(args.out)
            print(f"Enhanced script written to: {output_path}")
        except Exception as e:
            print(f"Error enhancing script: {e}", file=sys.stderr)
            return 1
        
        # Generate README
        try:
            readme_path = hardener.generate_readme()
            print(f"README generated: {readme_path}")
        except Exception as e:
            print(f"Error generating README: {e}", file=sys.stderr)
            return 1
        
        # Run verification if requested
        if args.verify:
            self._run_verification(args.script)
        
        return 0
    
    def _handle_repo_mode(self, args: argparse.Namespace, notes: Optional[str]) -> int:
        """Handle repository mode.
        
        Args:
            args: Parsed command line arguments
            notes: Additional notes to include
            
        Returns:
            Exit code
        """
        print("Analyzing repository...")
        
        hardener = RepoHardener()
        
        # Detect project files
        try:
            detected = hardener.detect_project_files()
            print("Detected project files:")
            for file_type, files in detected.items():
                if files:
                    print(f"  {file_type}: {', '.join(files)}")
        except Exception as e:
            print(f"Error detecting project files: {e}", file=sys.stderr)
            return 1
        
        # Generate README
        try:
            output_path = args.out or "README.md"
            if hasattr(args, 'openai') and args.openai:
                readme_path = hardener.generate_readme_with_openai(output_path, notes)
                print(f"README generated with OpenAI: {readme_path}")
            else:
                readme_path = hardener.generate_readme(output_path, notes)
                print(f"README generated: {readme_path}")
        except Exception as e:
            print(f"Error generating README: {e}", file=sys.stderr)
            return 1
        
        # Run verification if requested
        if args.verify:
            self._run_verification(".")
        
        return 0
    
    def _run_verification(self, target: str) -> None:
        """Run verification tools on the target.
        
        Args:
            target: Target file or directory to verify
        """
        print("\nRunning verification...")
        
        # Try to run black
        try:
            result = subprocess.run(['black', '--check', target], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✓ Black formatting check passed")
            else:
                print("✗ Black formatting issues found")
                print(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("Black not available or timed out")
        
        # Try to run ruff
        try:
            result = subprocess.run(['ruff', 'check', target], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✓ Ruff linting check passed")
            else:
                print("✗ Ruff linting issues found")
                print(result.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("Ruff not available or timed out")
        
        # Show help output for the enhanced script
        if os.path.isfile(target) and target.endswith('.py'):
            try:
                result = subprocess.run([sys.executable, target, '--help'], 
                                      capture_output=True, text=True, timeout=10)
                print(f"\n--help output for {target}:")
                print(result.stdout)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print(f"Could not run --help for {target}")


def main() -> int:
    """Main entry point for the CLI application.
    
    Returns:
        Exit code
    """
    cli = READMEHardenerCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())