import os
import hashlib
import requests
from urllib.parse import urlparse, unquote
from pathlib import Path


class UbuntuImageFetcher:
    """
    A respectful image fetcher that embodies Ubuntu philosophy
    """
    
    def __init__(self, download_dir="Fetched_Images"):
        self.download_dir = Path(download_dir)
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit
        self.timeout = 10
        self.downloaded_hashes = {}
        
        # Create directory if it doesn't exist
        self.download_dir.mkdir(exist_ok=True)
        
    def get_safe_filename(self, url, content_type=None):
        """
        Extract a safe filename from URL or generate fallback
        """
        parsed = urlparse(url)
        filename = unquote(os.path.basename(parsed.path))
        
        # If no filename or extension, generate fallback
        if not filename or '.' not in filename:
            extension = self._get_extension_from_content_type(content_type)
            filename = f"downloaded_image{extension}"
        
        # Sanitize filename - remove unsafe characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        filename = ''.join(c if c in safe_chars else '_' for c in filename)
        
        return filename
    
    def _get_extension_from_content_type(self, content_type):
        """
        Get file extension from content type
        """
        if not content_type:
            return ".jpg"
        
        extensions = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/bmp': '.bmp',
            'image/svg+xml': '.svg'
        }
        return extensions.get(content_type.lower(), '.jpg')
    
    def get_unique_filename(self, filename):
        """
        Handle duplicate filenames by appending suffix
        """
        filepath = self.download_dir / filename
        
        if not filepath.exists():
            return filename
            
        # File exists, create unique name
        stem = filepath.stem
        suffix = filepath.suffix
        counter = 1
        
        while True:
            new_filename = f"{stem}_{counter}{suffix}"
            new_filepath = self.download_dir / new_filename
            if not new_filepath.exists():
                return new_filename
            counter += 1
    
    def calculate_file_hash(self, content):
        """
        Calculate SHA256 hash of file content
        """
        return hashlib.sha256(content).hexdigest()
    
    def is_duplicate_content(self, content, filename):
        """
        Check if content is duplicate based on hash
        """
        file_hash = self.calculate_file_hash(content)
        
        if file_hash in self.downloaded_hashes:
            existing_file = self.downloaded_hashes[file_hash]
            print(f"  Content identical to already downloaded: {existing_file}")
            return True
            
        self.downloaded_hashes[file_hash] = filename
        return False
    
    def validate_image_response(self, response, url):
        """
        Validate that the response contains a valid image
        """
        # Check content type
        content_type = response.headers.get('Content-Type', '').lower()
        if not content_type.startswith('image/'):
            raise ValueError(f"URL does not point to an image. Content-Type: {content_type}")
        
        # Check content length
        content_length = response.headers.get('Content-Length')
        if content_length and int(content_length) > self.max_file_size:
            size_mb = int(content_length) / (1024 * 1024)
            raise ValueError(f"Image too large: {size_mb:.1f}MB (max: {self.max_file_size // (1024 * 1024)}MB)")
        
        return content_type
    
    def fetch_single_image(self, url):
        """
        Fetch a single image from URL
        """
        try:
            print(f" Connecting to: {url}")
            
            # Make request with timeout
            response = requests.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # Validate response
            content_type = self.validate_image_response(response, url)
            
            # Get filename
            filename = self.get_safe_filename(url, content_type)
            
            # Download content
            content = response.content
            
            # Check for duplicate content
            if self.is_duplicate_content(content, filename):
                return False
            
            # Get unique filename
            unique_filename = self.get_unique_filename(filename)
            filepath = self.download_dir / unique_filename
            
            # Save file
            with open(filepath, 'wb') as f:
                f.write(content)
            
            # Success messages
            print(f"✓ Successfully fetched: {filename}")
            print(f"✓ Image saved to {filepath}")
            print()
            
            return True
            
        except requests.exceptions.Timeout:
            print(f" Connection timeout for: {url}")
            print("   The community server didn't respond in time. Please try again later.")
            
        except requests.exceptions.ConnectionError:
            print(f"  Cannot connect to: {url}")
            print("   Please check your internet connection and the URL.")
            
        except requests.exceptions.HTTPError as e:
            print(f"  Server responded with error for: {url}")
            print(f"   HTTP {e.response.status_code}: {e.response.reason}")
            
        except ValueError as e:
            print(f"  Invalid image at: {url}")
            print(f"   {str(e)}")
            
        except Exception as e:
            print(f"  Unexpected error with: {url}")
            print(f"   {str(e)}")
        
        print()
        return False
    
    def fetch_images(self, urls):
        """
        Fetch multiple images from URLs
        """
        if isinstance(urls, str):
            urls = [url.strip() for url in urls.split(',')]
        
        successful = 0
        total = len(urls)
        
        for url in urls:
            url = url.strip()
            if url:
                if self.fetch_single_image(url):
                    successful += 1
        
        return successful, total


def main():
    """
    Main function - Ubuntu Image Fetcher
    """
    print(" Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web")
    print()
    print('"I am because we are." - Ubuntu Philosophy')
    print()
    
    # Get user input
    urls_input = input("Please enter the image URL(s) (comma-separated for multiple): ").strip()
    
    if not urls_input:
        print("  No URLs provided. Ubuntu teaches us to share - please provide URLs to fetch.")
        return
    
    print()
    
    # Initialize fetcher
    fetcher = UbuntuImageFetcher()
    
    # Fetch images
    successful, total = fetcher.fetch_images(urls_input)
    
    # Summary message
    if successful == total and total > 0:
        print(" All images fetched successfully!")
    elif successful > 0:
        print(f"Fetched {successful} out of {total} images successfully.")
    else:
        print(" No images could be fetched. The community connection was not established this time.")
    
    print()
    print("Connection strengthened. Community enriched.")
    print()
    print("Ubuntu reminds us: 'A person is a person through other persons.'")


if __name__ == "__main__":
    main()