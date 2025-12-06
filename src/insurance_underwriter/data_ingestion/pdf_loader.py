"""
PDF Loader Module

This module provides functionality to load, parse, summarize PDFs and save summaries.
"""

import os
from pathlib import Path
from typing import Optional

from ..utils.helpers import parse_pdf, split_into_chunks, summarize


def load_existing_summary(file_name: str, output_dir: str = "data/output") -> Optional[str]:
    """
    Load an existing summary file if it exists.
    
    Args:
        file_name: Name of the PDF file (with or without .pdf extension)
        output_dir: Directory containing the summary files (relative to project root)
        
    Returns:
        Content of the existing summary file, or None if file doesn't exist
    """
    # Get the project root
    project_root = Path(__file__).parent.parent.parent.parent
    
    # Ensure file has .pdf extension for processing
    if not file_name.endswith('.pdf'):
        file_name += '.pdf'
    
    # Generate summary filename
    base_name = Path(file_name).stem  # Remove .pdf extension
    summary_filename = f"{base_name}_summary.txt"
    summary_path = project_root / output_dir / summary_filename
    
    try:
        if summary_path.exists():
            with open(summary_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        return None
    except Exception as e:
        print(f"Error reading summary file {summary_path}: {e}")
        return None


def process_and_summarize_pdf(file_name: str, source_dir: str = "data/source", 
                             output_dir: str = "data/output", 
                             chunk_size: int = 512, 
                             chunk_overlap: int = 200,
                             max_summary_length: int = 150,
                             force_reprocess: bool = False) -> Optional[str]:
    """
    Process a PDF file by parsing, summarizing, and saving the summary.
    If a summary file already exists, it will be loaded instead of reprocessing the PDF.
    
    Args:
        file_name: Name of the PDF file (with or without .pdf extension)
        source_dir: Directory containing the source PDF files (relative to project root)
        output_dir: Directory to save the summary file (relative to project root)
        chunk_size: Maximum characters per chunk for text splitting
        chunk_overlap: Number of overlapping characters between chunks
        max_summary_length: Maximum length of each summary chunk
        force_reprocess: If True, reprocess PDF even if summary exists
        
    Returns:
        Path to the existing or created summary file, or None if processing failed
        
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: If processing fails
    """
    # Get the project root (assuming this file is in src/insurance_underwriter/data_ingestion/)
    project_root = Path(__file__).parent.parent.parent.parent
    
    # Ensure file has .pdf extension
    if not file_name.endswith('.pdf'):
        file_name += '.pdf'
    
    # Construct file paths
    pdf_path = project_root / source_dir / file_name
    output_path = project_root / output_dir
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate output filename
    base_name = Path(file_name).stem  # Remove .pdf extension
    summary_filename = f"{base_name}_summary.txt"
    summary_path = output_path / summary_filename
    
    # Check if summary already exists and load it if not forcing reprocess
    if summary_path.exists() and not force_reprocess:
        print(f"Summary already exists: {summary_path}")
        print("Loading existing summary...")
        try:
            with open(summary_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"Loaded existing summary ({len(content)} characters)")
            return str(summary_path)
        except Exception as e:
            print(f"Warning: Could not read existing summary file: {e}")
            print("Proceeding with reprocessing...")
    
    try:
        # Check if PDF file exists
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"Processing PDF: {pdf_path}")
        
        # Parse PDF content
        pdf_text = parse_pdf(str(pdf_path))
        
        if not pdf_text.strip():
            print("Warning: No text content extracted from PDF")
            return None
        
        print(f"Extracted {len(pdf_text)} characters from PDF")
        
        # Split into chunks
        text_chunks = split_into_chunks(pdf_text, chunk_size, chunk_overlap)
        print(f"Split text into {len(text_chunks)} chunks")
        
        # Generate summaries
        print("Generating summaries...")
        summaries = summarize(text_chunks, max_summary_length)
        
        # Combine summaries
        combined_summary = "\n\n".join(summaries)
        
        # Write to output file
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"Summary of {file_name}\n")
            f.write("=" * (len(file_name) + 11) + "\n\n")
            f.write(combined_summary)
        
        print(f"Summary saved to: {summary_path}")
        return str(summary_path)
        
    except Exception as e:
        print(f"Error processing PDF {file_name}: {str(e)}")
        raise