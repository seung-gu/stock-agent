"""이미지 처리 서비스 - 로컬 이미지 찾기 및 클라우드 업로드"""

import os
import io
import time
import re
import glob
import boto3
from typing import Dict
from PIL import Image
from dotenv import load_dotenv

load_dotenv(override=True)


def find_local_images(content: str) -> tuple[str, list[str], dict[str, str]]:
    """Find local image files in markdown content. Returns (processed_content, image_files, image_map) where:
    - processed_content: content with image links replaced by placeholders
    - image_files: list of found image file paths
    - image_map: mapping of file_path to alt_text or link_text
    """
    processed_content = content
    image_files = []
    image_map = {}  # {file_path: alt_text} mapping
    processed_paths = set()  # Track which paths we've already replaced

    # Parse all image patterns: sandbox links and Chart saved: patterns
    patterns = [
        (r'!\[([^\]]*)\]\(sandbox:([^)]+)\)', lambda m: (m.group(2), m.group(1), f'![{m.group(1)}](sandbox:{m.group(2)})')),  # Image links
        (r'\[([^\]]+)\]\(sandbox:([^)]+)\)', lambda m: (m.group(2), m.group(1), f'[{m.group(1)}](sandbox:{m.group(2)})')),  # Normal links
        (r'Chart saved:\s+([^\s\n]+\.(?:png|jpg|jpeg))', lambda m: (m.group(1).strip(), None, f'Chart saved: {m.group(1).strip()}'))  # Chart saved pattern
    ]
    
    for pattern, extractor in patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            file_path, alt_text, original_text = extractor(match)
            
            # For Chart saved pattern, check if file exists before adding to image_files
            # But always replace placeholder regardless of file existence
            is_chart_saved = 'Chart saved' in pattern
            file_exists = os.path.exists(file_path) if is_chart_saved else True
            
            if file_path not in image_files and file_exists:
                image_files.append(file_path)
            
            if file_path not in image_map:
                if alt_text:
                    image_map[file_path] = alt_text
                else:
                    # Use filename as alt text for Chart saved pattern
                    filename = os.path.basename(file_path)
                    image_map[file_path] = filename.replace('_', ' ').replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
            
            # Replace in content if not already replaced (always replace, even if file doesn't exist)
            if file_path not in processed_paths:
                processed_content = processed_content.replace(
                    original_text,
                    f'{{{{IMAGE_PLACEHOLDER:{file_path}}}}}',
                    1
                )
                processed_paths.add(file_path)

    # 4. Additionally, search common temp directories for chart images that weren't in the content
    # NOTE: The following patterns cover both Linux (/tmp/market_charts_*) and macOS (/var/folders/*/T/market_charts_*)
    # This ensures chart images are found regardless of OS, since tempfile.mkdtemp(prefix="market_charts_")
    # creates different paths depending on the environment.
    # On macOS, charts are typically saved in /var/folders/.../T/market_charts_xxxxx
    # On Linux or some environments, charts are saved in /tmp/market_charts_xxxxx
    for pattern in ['/tmp/market_charts_*', '/var/folders/*/T/market_charts_*']:
        dirs = glob.glob(pattern)
        if dirs:
            # Get the most recent directory
            latest_dir = max(dirs, key=os.path.getmtime)
            chart_files = glob.glob(f'{latest_dir}/*.png')
            if chart_files:  # Only process and break if PNG files were actually found
                for chart_file in chart_files:
                    if chart_file not in image_files:
                        image_files.append(chart_file)
                        # Add to image_map with filename as alt text
                        filename = os.path.basename(chart_file)
                        image_map[chart_file] = filename.replace('_', ' ').replace('.png', '')
                break  # Only break if files were found, otherwise check next pattern

    return processed_content, image_files, image_map


def upload_images_to_cloudflare(image_files: list[str]) -> dict[str, str]:
    """Uploads images to Cloudflare R2 and returns a mapping {file_path: url}."""
    uploaded_map = {}
    r2_client = boto3.client('s3',
        endpoint_url=f'https://{os.environ["R2_ACCOUNT_ID"]}.r2.cloudflarestorage.com',
        aws_access_key_id=os.environ['R2_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['R2_SECRET_ACCESS_KEY'],
        region_name='auto'
    )
    CHART_IMAGE_SIZE = (600, 400)
    CHART_IMAGE_QUALITY = 100

    # Upload all chart files as thumbnails
    for chart_file in image_files:
        try:
            print(f"🔄 Starting R2 upload: {chart_file}")
            filename = os.path.basename(chart_file)
            # Open the image and resize to thumbnail
            with Image.open(chart_file) as img:
                img.thumbnail(CHART_IMAGE_SIZE, Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                # Convert image to RGB and save as JPEG
                img.convert('RGB').save(buffer, format='JPEG', quality=CHART_IMAGE_QUALITY, optimize=True)
                buffer.seek(0)

                object_key = f"charts/{filename.replace('.png', f'_{int(time.time())}.jpg')}"
                print(f"📤 Uploading to R2: {object_key}")
                # 파일 크기 확인
                file_size_kb = len(buffer.getvalue()) / 1024
                print(f"📏 Image size: {file_size_kb:.1f} KB")
                
                r2_client.upload_fileobj(buffer, os.environ['R2_BUCKET_NAME'], object_key,
                    ExtraArgs={'ContentType': 'image/jpeg'})

                image_url = f"{os.environ['R2_PUBLIC_URL']}/{object_key}"
                uploaded_map[chart_file] = image_url
                print(f"✅ R2 upload successful: {filename} -> {image_url}")
        except Exception as e:
            print(f"❌ R2 upload failed: {chart_file} - {e}")

    return uploaded_map

