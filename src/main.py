
"""
Insurance Underwriter - Main Entry Point

This script provides the main entry point for the insurance underwriter application.
It processes PDF files by parsing, summarizing, and saving the results.
"""

import argparse
import os
import sys
from pathlib import Path

# Add the src directory to Python path for imports
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from insurance_underwriter.data_ingestion.pdf_loader import process_and_summarize_pdf


def main():
    """
    Main function to process PDF files for insurance underwriting.
    
    Supports both command-line arguments and interactive mode.
    """
    parser = argparse.ArgumentParser(
        description="Insurance Underwriter PDF Processing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --file policy.pdf
  python main.py --file policy.pdf --source custom_source --output custom_output
  python main.py  # Interactive mode
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='PDF file name to process (with or without .pdf extension)'
    )
    
    parser.add_argument(
        '--source', '-s',
        type=str,
        default='data/source',
        help='Source directory containing PDF files (default: data/source)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='data/output',
        help='Output directory for summary files (default: data/output)'
    )
    
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=512,
        help='Text chunk size for processing (default: 512)'
    )
    
    parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=200,
        help='Text chunk overlap (default: 200)'
    )
    
    parser.add_argument(
        '--max-summary',
        type=int,
        default=150,
        help='Maximum summary length (default: 150)'
    )
    
    parser.add_argument(
        '--force-reprocess',
        action='store_true',
        help='Force reprocessing even if summary file already exists'
    )
    
    args = parser.parse_args()
    
    try:
        if args.file:
            # Process specified file
            process_single_file(args)
        else:
            # Interactive mode
            interactive_mode(args)
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


def process_single_file(args):
    """Process a single PDF file."""
    print(f"Processing PDF file: {args.file}")
    print("-" * 50)
    
    summary_path = process_and_summarize_pdf(
        file_name=args.file,
        source_dir=args.source,
        output_dir=args.output,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        max_summary_length=args.max_summary,
        force_reprocess=args.force_reprocess
    )
    
    if summary_path:
        print(f"\n✅ Successfully processed: {args.file}")
        print(f"📄 Summary saved to: {summary_path}")
    else:
        print(f"\n❌ Failed to process: {args.file}")


def interactive_mode(args):
    """Interactive mode for processing multiple files."""
    print("🔧 Insurance Underwriter PDF Processor")
    print("=" * 50)
    print("Interactive mode - Enter PDF filenames to process")
    print("Type 'quit' or 'exit' to stop, 'list' to show available files\n")
    
    while True:
        try:
            filename = input("Enter PDF filename (or command): ").strip()
            
            if not filename:
                continue
                
            if filename.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if filename.lower() == 'list':
                list_available_files(args.source)
                continue
                
            print(f"\n🔄 Processing: {filename}")
            print("-" * 30)
            
            summary_path = process_and_summarize_pdf(
                file_name=filename,
                source_dir=args.source,
                output_dir=args.output,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap,
                max_summary_length=args.max_summary,
                force_reprocess=args.force_reprocess
            )
            
            if summary_path:
                print(f"✅ Success! Summary saved to: {summary_path}\n")
            else:
                print(f"❌ Failed to process: {filename}\n")
                
        except EOFError:
            print("\n👋 Goodbye!")
            break


def list_available_files(source_dir):
    """List available PDF files in the source directory."""
    project_root = Path(__file__).parent.parent
    source_path = project_root / source_dir
    
    if not source_path.exists():
        print(f"📂 Source directory not found: {source_path}")
        print(f"   Please create it and add PDF files to process.")
        return
    
    pdf_files = list(source_path.glob("*.pdf"))
    
    if pdf_files:
        print(f"📂 Available PDF files in {source_dir}:")
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"   {i}. {pdf_file.name}")
    else:
        print(f"📂 No PDF files found in {source_dir}")
    print()


if __name__ == "__main__":
    main()