import os
import re
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def is_binary(file_path):
    """Check if a file is binary."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)
        return False
    except UnicodeDecodeError:
        return True
    except Exception as e:
        print(f"Warning: Could not check if {file_path} is binary: {e}")
        return True

def should_ignore(file_path, ignore_patterns):
    """Check if the file or directory should be ignored."""
    for pattern in ignore_patterns:
        if re.search(pattern, file_path):
            return True
    return False

def collect_files(root_dir, ignore_patterns):
    """Collect all non-binary files from the codebase, skipping ignored paths."""
    all_files = []
    
    try:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Remove ignored directories
            dirnames[:] = [d for d in dirnames if not should_ignore(os.path.join(dirpath, d), ignore_patterns)]
            
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                
                # Skip ignored files
                if should_ignore(file_path, ignore_patterns):
                    continue
                    
                try:
                    # Skip binary files
                    if is_binary(file_path):
                        continue
                        
                    # Get relative path from root_dir
                    rel_path = os.path.relpath(file_path, root_dir)
                    
                    all_files.append((rel_path, file_path))
                except Exception as e:
                    print(f"Warning: Skipping file {file_path}: {e}")
        
        # Sort files by their path
        all_files.sort(key=lambda x: x[0])
        return all_files
    except Exception as e:
        print(f"Error scanning directory {root_dir}: {e}")
        return all_files

def create_pdf(files, output_pdf):
    """Create a PDF with all the code files."""
    try:
        # Ensure directory exists
        output_dir = os.path.dirname(output_pdf)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        doc = SimpleDocTemplate(output_pdf, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Create a custom style for file paths
        file_path_style = ParagraphStyle(
            'FilePathStyle',
            parent=styles['Heading2'],
            spaceAfter=12,
            spaceBefore=24,
            textColor='#1F497D',
        )
        
        # Create a custom monospace style for code
        code_style = ParagraphStyle(
            'CodeStyle',
            parent=styles['Code'],
            fontName='Courier',
            fontSize=8,
            leading=10,
            spaceAfter=12,
        )
        
        # Build the PDF content
        elements = []
        
        # Add a title
        title = Paragraph("Source Code Documentation", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.5 * inch))
        
        # Process each file
        for rel_path, abs_path in files:
            try:
                # Add the file path
                path_para = Paragraph(rel_path, file_path_style)
                elements.append(path_para)
                
                # Add the file content
                with open(abs_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Use Preformatted to preserve whitespace and indentation
                code_para = Preformatted(content, code_style)
                elements.append(code_para)
                
                # Add a spacer between files
                elements.append(Spacer(1, 0.25 * inch))
                
            except Exception as e:
                print(f"Error processing file {rel_path}: {e}")
        
        # Build the PDF
        doc.build(elements)
        return True
    except PermissionError as e:
        print(f"Permission error: {e}")
        print("You might not have write permission for this location or the file is currently open in another program.")
        return False
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False

def get_valid_directory():
    """Get a valid directory path from the user with retry logic."""
    while True:
        root_dir = input("Enter the path to your codebase: ").strip()
        if os.path.isdir(root_dir):
            return root_dir
        else:
            print(f"Error: '{root_dir}' is not a valid directory.")
            retry = input("Would you like to try again? (y/n): ").strip().lower()
            if retry != 'y':
                print("Exiting program.")
                sys.exit(0)

def get_valid_output_path(default_pdf):
    """Get a valid output file path from the user with retry logic."""
    while True:
        output_prompt = f"Enter the path for the output PDF (default: {default_pdf}): "
        output_pdf = input(output_prompt).strip() or default_pdf
        
        # If it's a directory, suggest a file in that directory
        if os.path.isdir(output_pdf):
            print(f"'{output_pdf}' is a directory, not a file.")
            new_pdf = os.path.join(output_pdf, "codebase.pdf")
            retry = input(f"Use '{new_pdf}' instead? (y/n): ").strip().lower()
            if retry == 'y':
                output_pdf = new_pdf
            else:
                continue
                
        # Ensure output path ends with .pdf
        if not output_pdf.lower().endswith('.pdf'):
            output_pdf += '.pdf'
            
        # Check if we can write to this location
        try:
            output_dir = os.path.dirname(output_pdf)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            # Test if we can write to the file
            with open(output_pdf, 'a'):
                pass
            
            # Remove the test file if it was newly created
            if os.path.exists(output_pdf) and os.path.getsize(output_pdf) == 0:
                os.remove(output_pdf)
                
            return output_pdf
            
        except (PermissionError, OSError) as e:
            print(f"Error: Cannot write to '{output_pdf}'. {e}")
            retry = input("Would you like to try another location? (y/n): ").strip().lower()
            if retry != 'y':
                print("Exiting program.")
                sys.exit(0)

def main():
    try:
        # Get valid input directory
        root_dir = get_valid_directory()

        # Default output PDF name
        default_pdf = os.path.join(os.path.dirname(root_dir), f"{os.path.basename(root_dir)}_code.pdf")
        
        # Get valid output path
        output_pdf = get_valid_output_path(default_pdf)
        
        # Get ignore patterns
        default_ignore_patterns = [
            r'venv/',
            r'\.git/',
            r'__pycache__/',
            r'\.vscode/',
            r'\.idea/',
            r'node_modules/',
            r'\.env',
            r'\.DS_Store',
            r'\.pyc$',
            r'\.pyo$',
            r'\.pyd$',
            r'\.so$',
            r'\.dll$',
            r'\.exe$',
            r'\.bin$',
        ]
        
        # Allow user to add additional ignore patterns
        print("\nDefault ignore patterns:", ', '.join(default_ignore_patterns))
        additional_patterns = input("Enter additional ignore patterns (comma-separated, leave empty for none): ")
        
        ignore_patterns = default_ignore_patterns
        if additional_patterns:
            ignore_patterns.extend([p.strip() for p in additional_patterns.split(',')])
        
        print(f"\nScanning codebase at {root_dir}...")
        files = collect_files(root_dir, ignore_patterns)
        
        if not files:
            print("No files found matching the criteria.")
            retry = input("Would you like to try with different ignore patterns? (y/n): ").strip().lower()
            if retry == 'y':
                main()  # Restart the process
            return
        
        print(f"Found {len(files)} files. Creating PDF at {output_pdf}...")
        success = create_pdf(files, output_pdf)
        
        if success:
            print(f"PDF created successfully at {output_pdf}")
        else:
            print("Failed to create PDF. See errors above.")
            retry = input("Would you like to try again with a different output location? (y/n): ").strip().lower()
            if retry == 'y':
                output_pdf = get_valid_output_path(default_pdf)
                print(f"Trying again to create PDF at {output_pdf}...")
                if create_pdf(files, output_pdf):
                    print(f"PDF created successfully at {output_pdf}")
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        retry = input("Would you like to restart the program? (y/n): ").strip().lower()
        if retry == 'y':
            main()  # Restart the process

if __name__ == "__main__":
    main()