# Functions
"""
Insurance Underwriter Utility Functions

This module provides essential PDF processing capabilities:
- PDF text extraction
- Text chunking with configurable strategies  
- Text summarization using transformer models
"""

import os
import tempfile
from typing import List, Union

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import pipeline


def parse_pdf(file_path: Union[str, bytes]) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        file_path: Path to PDF file (str) or PDF file content as bytes
        
    Returns:
        Extracted text as a single string
        
    Raises:
        FileNotFoundError: If PDF file doesn't exist
        Exception: If PDF parsing fails
    """
    if isinstance(file_path, bytes):
        # Handle bytes input by writing to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(file_path)
            temp_path = temp_file.name
        
        try:
            loader = PyPDFLoader(temp_path)
            pages = loader.load()
            return "\n\n".join(page.page_content for page in pages)
        finally:
            os.unlink(temp_path)
    
    else:
        # Handle file path input
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        print('pdf output')
        print("\n\n".join(page.page_content for page in pages))
        return "\n\n".join(page.page_content for page in pages)


def split_into_chunks(text: str, chunk_size: int = 512, chunk_overlap: int = 200) -> List[str]:
    """
    Split text into manageable chunks for processing.
    
    Args:
        text: Input text to split
        chunk_size: Maximum characters per chunk
        chunk_overlap: Number of overlapping characters between chunks
        
    Returns:
        List of text chunks
    """
    if not text.strip():
        return []
    
    # Ensure chunk_overlap is not larger than chunk_size
    actual_overlap = min(chunk_overlap, chunk_size // 2)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=actual_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    return splitter.split_text(text)


def summarize(chunks: List[str], max_length: int = 150) -> List[str]:
    """
    Generate summaries for text chunks using BART model.
    
    Args:
        chunks: List of text chunks to summarize
        max_length: Maximum length of each summary
        
    Returns:
        List of summary strings corresponding to input chunks
        
    Raises:
        Exception: If summarization model fails to load or process
    """
    if not chunks:
        return []
    
    summarizer = pipeline(
        "summarization", 
        model="facebook/bart-large-cnn",
        device=-1  # Use CPU
    )
    
    summaries = []
    for chunk in chunks:
        # Skip very short chunks that don't need summarization
        if len(chunk.strip()) < 50:
            summaries.append(chunk.strip())
            continue
            
        try:
            # Dynamically adjust max_length based on input length
            # For summarization, output should be shorter than input
            input_length = len(chunk.split())  # Count words for better estimation
            dynamic_max_length = min(max_length, max(20, input_length // 2))
            dynamic_min_length = min(10, dynamic_max_length // 2)
            
            result = summarizer(
                chunk, 
                max_length=dynamic_max_length, 
                min_length=dynamic_min_length,
                do_sample=False,
                truncation=True
            )
            summaries.append(result[0]['summary_text'])
        except Exception as e:
            # Fallback to original text if summarization fails
            summaries.append(f"Summarization failed: {chunk[:100]}...")
    
    return summaries