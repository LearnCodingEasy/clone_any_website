from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse, unquote
import time
import base64
import traceback
import os
import mimetypes
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Thread-safe counter for progress tracking
download_progress = {'current': 0, 'total': 0, 'lock': threading.Lock()}


@api_view(['POST'])
def scrape_website(request):
    """
    Complete website cloner - 100% of everything with perfect structure
    """
    try:
        url = request.data.get('url')

        if not url:
            return Response(
                {'error': 'URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        print(f"🚀 Starting complete website clone: {url}")

        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }

        # Fetch the main webpage
        print("📄 Fetching main HTML...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Initialize progress tracking
        with download_progress['lock']:
            download_progress['current'] = 0
            download_progress['total'] = 0

        print("🔍 Analyzing website structure...")

        # Extract ALL resources with complete structure
        all_resources = extract_all_resources(soup, url, headers)

        # Process HTML and update links to local files
        processed_html = process_html_links(soup, all_resources, url)

        print(f"✅ Complete! Extracted {len(all_resources)} total files")

        return Response({
            'html': str(processed_html),
            'resources': all_resources,
            'url': url,
            'title': soup.title.string if soup.title else 'Untitled',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'stats': {
                'total_files': len(all_resources),
                'css_files': len([r for r in all_resources if r['category'] == 'css']),
                'js_files': len([r for r in all_resources if r['category'] == 'javascript']),
                'images': len([r for r in all_resources if r['category'] == 'image']),
                'fonts': len([r for r in all_resources if r['category'] == 'font']),
                'libraries': len([r for r in all_resources if r['category'] == 'library']),
                'other': len([r for r in all_resources if r['category'] == 'other'])
            }
        })

    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {str(e)}")
        return Response(
            {'error': f'Failed to fetch website: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        print(f"❌ General error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return Response(
            {'error': f'Scraping failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def extract_all_resources(soup, base_url, headers):
    """
    Extract 100% of all resources from the website
    """
    all_resources = []
    resource_urls = set()  # Prevent duplicates

    print("🎯 Discovering all resources...")

    # 1. CSS FILES - All stylesheets
    css_resources = discover_css_resources(soup, base_url)
    all_resources.extend(css_resources)
    resource_urls.update([r['url']
                         for r in css_resources if r['url'] != 'inline'])

    # 2. JAVASCRIPT FILES - All scripts
    js_resources = discover_js_resources(soup, base_url)
    all_resources.extend(js_resources)
    resource_urls.update([r['url']
                         for r in js_resources if r['url'] != 'inline'])

    # 3. IMAGES - All images from everywhere
    image_resources = discover_all_images(soup, base_url)
    all_resources.extend(image_resources)
    resource_urls.update(
        [r['url'] for r in image_resources if not r['url'].startswith('data:')])

    # 4. FONTS - All font files
    font_resources = discover_font_resources(soup, base_url)
    all_resources.extend(font_resources)
    resource_urls.update([r['url'] for r in font_resources])

    # 5. OTHER RESOURCES - Videos, audio, documents, etc.
    other_resources = discover_other_resources(soup, base_url)
    all_resources.extend(other_resources)
    resource_urls.update([r['url'] for r in other_resources])

    # 6. DEEP CSS ANALYSIS - Extract resources from CSS files
    css_embedded_resources = extract_resources_from_css(
        all_resources, base_url)
    all_resources.extend(css_embedded_resources)

    print(f"📊 Found {len(all_resources)} total resources")

    # Download all resources with threading
    download_all_resources(all_resources, headers)

    return all_resources


def discover_css_resources(soup, base_url):
    """
    Discover all CSS resources
    """
    css_resources = []

    # Inline styles
    style_tags = soup.find_all('style')
    for i, style in enumerate(style_tags):
        if style.string and style.string.strip():
            css_resources.append({
                'filename': f'inline-styles-{i+1}.css',
                'original_path': f'css/inline-styles-{i+1}.css',
                'url': 'inline',
                'content': style.string.strip(),
                'category': 'css',
                'type': 'inline',
                'size': len(style.string.strip()),
                'downloaded': True
            })

    # External stylesheets
    link_tags = soup.find_all('link')
    for link in link_tags:
        href = link.get('href')
        rel = link.get('rel', [])

        if href and ('stylesheet' in rel or 'preload' in rel):
            full_url = urljoin(base_url, href)
            original_path = clean_path(href)

            # Ensure CSS extension
            if not original_path.endswith('.css'):
                original_path += '.css'

            css_resources.append({
                'filename': os.path.basename(original_path),
                'original_path': original_path,
                'url': full_url,
                'content': '',
                'category': 'css',
                'type': 'external',
                'size': 0,
                'downloaded': False
            })

    return css_resources


def discover_js_resources(soup, base_url):
    """
    Discover all JavaScript resources
    """
    js_resources = []

    # All script tags
    script_tags = soup.find_all('script')
    inline_count = 0

    for i, script in enumerate(script_tags):
        if script.string and script.string.strip():
            # Inline JavaScript
            inline_count += 1
            js_resources.append({
                'filename': f'inline-script-{inline_count}.js',
                'original_path': f'js/inline-script-{inline_count}.js',
                'url': 'inline',
                'content': script.string.strip(),
                'category': 'javascript',
                'type': 'inline',
                'size': len(script.string.strip()),
                'downloaded': True
            })
        elif script.get('src'):
            # External JavaScript
            src = script.get('src')
            full_url = urljoin(base_url, src)
            original_path = clean_path(src)

            # Ensure JS extension
            if not original_path.endswith('.js'):
                original_path += '.js'

            # Determine if it's a library or regular script
            category = 'library' if is_library_url(full_url) else 'javascript'

            js_resources.append({
                'filename': os.path.basename(original_path),
                'original_path': original_path,
                'url': full_url,
                'content': '',
                'category': category,
                'type': 'external',
                'size': 0,
                'downloaded': False
            })

    return js_resources


def discover_all_images(soup, base_url):
    """
    Discover ALL images from everywhere
    """
    image_resources = []
    image_urls = set()

    # 1. IMG tags
    img_tags = soup.find_all('img')
    for img in img_tags:
        src = img.get('src') or img.get(
            'data-src') or img.get('data-lazy-src') or img.get('data-original')
        if src and src not in image_urls:
            image_urls.add(src)
            image_resources.append(create_image_resource(
                src, base_url, img.get('alt', '')))

    # 2. Picture/source tags
    source_tags = soup.find_all('source')
    for source in source_tags:
        srcset = source.get('srcset') or source.get('data-srcset')
        if srcset:
            # Parse srcset (can contain multiple URLs)
            urls = parse_srcset(srcset)
            for url in urls:
                if url and url not in image_urls:
                    image_urls.add(url)
                    image_resources.append(
                        create_image_resource(url, base_url))

    # 3. CSS background images (from style attributes)
    elements_with_style = soup.find_all(attrs={'style': True})
    for element in elements_with_style:
        style = element.get('style', '')
        bg_images = re.findall(
            r'background-image:\s*url$$["\']?([^"\']+)["\']?$$', style)
        for bg_url in bg_images:
            if bg_url and bg_url not in image_urls:
                image_urls.add(bg_url)
                image_resources.append(create_image_resource(
                    bg_url, base_url, 'Background image'))

    # 4. Link tags for icons
    link_tags = soup.find_all('link')
    for link in link_tags:
        rel = link.get('rel', [])
        href = link.get('href')

        if href and any(icon_type in rel for icon_type in ['icon', 'apple-touch-icon', 'shortcut']):
            if href not in image_urls:
                image_urls.add(href)
                image_resources.append(
                    create_image_resource(href, base_url, 'Icon'))

    # 5. Meta tags for social media images
    meta_tags = soup.find_all('meta')
    for meta in meta_tags:
        property_val = meta.get('property', '') or meta.get('name', '')
        content = meta.get('content', '')

        if content and any(prop in property_val for prop in ['og:image', 'twitter:image', 'image']):
            if content not in image_urls:
                image_urls.add(content)
                image_resources.append(create_image_resource(
                    content, base_url, 'Social media image'))

    return image_resources


def discover_font_resources(soup, base_url):
    """
    Discover all font resources
    """
    font_resources = []

    # Link tags for fonts
    link_tags = soup.find_all('link')
    for link in link_tags:
        href = link.get('href')
        rel = link.get('rel', [])

        if href and ('preload' in rel or 'stylesheet' in rel):
            full_url = urljoin(base_url, href)

            # Check if it's a font URL
            if is_font_url(full_url) or 'font' in href.lower():
                original_path = clean_path(href)

                font_resources.append({
                    'filename': os.path.basename(original_path),
                    'original_path': original_path,
                    'url': full_url,
                    'content': '',
                    'category': 'font',
                    'type': 'external',
                    'size': 0,
                    'downloaded': False
                })

    return font_resources


def discover_other_resources(soup, base_url):
    """
    Discover other resources (videos, audio, documents, etc.)
    """
    other_resources = []

    # Video tags
    video_tags = soup.find_all('video')
    for video in video_tags:
        src = video.get('src')
        if src:
            other_resources.append(
                create_media_resource(src, base_url, 'video'))

        # Source tags within video
        source_tags = video.find_all('source')
        for source in source_tags:
            src = source.get('src')
            if src:
                other_resources.append(
                    create_media_resource(src, base_url, 'video'))

    # Audio tags
    audio_tags = soup.find_all('audio')
    for audio in audio_tags:
        src = audio.get('src')
        if src:
            other_resources.append(
                create_media_resource(src, base_url, 'audio'))

        # Source tags within audio
        source_tags = audio.find_all('source')
        for source in source_tags:
            src = source.get('src')
            if src:
                other_resources.append(
                    create_media_resource(src, base_url, 'audio'))

    # Embed and object tags
    embed_tags = soup.find_all(['embed', 'object'])
    for embed in embed_tags:
        src = embed.get('src') or embed.get('data')
        if src:
            other_resources.append(
                create_media_resource(src, base_url, 'other'))

    # Links to documents
    a_tags = soup.find_all('a', href=True)
    for a in a_tags:
        href = a.get('href')
        if href and is_document_url(href):
            other_resources.append(
                create_media_resource(href, base_url, 'document'))

    return other_resources


def extract_resources_from_css(css_resources, base_url):
    """
    Extract resources referenced in CSS files
    """
    embedded_resources = []

    for css_resource in css_resources:
        if css_resource['category'] == 'css' and css_resource.get('content'):
            css_content = css_resource['content']

            # Find all url() references in CSS
            url_matches = re.findall(
                r'url$$["\']?([^"\']+)["\']?$$', css_content)

            for url_match in url_matches:
                if not url_match.startswith('data:'):
                    full_url = urljoin(base_url, url_match)

                    # Determine resource type
                    if is_image_url(url_match):
                        category = 'image'
                    elif is_font_url(url_match):
                        category = 'font'
                    else:
                        category = 'other'

                    original_path = clean_path(url_match)

                    embedded_resources.append({
                        'filename': os.path.basename(original_path),
                        'original_path': original_path,
                        'url': full_url,
                        'content': '',
                        'category': category,
                        'type': 'css-embedded',
                        'size': 0,
                        'downloaded': False
                    })

    return embedded_resources


def download_all_resources(resources, headers):
    """
    Download all resources using threading for speed
    """
    to_download = [r for r in resources if not r['downloaded']
                   and r['url'] not in ['inline', 'data:embedded']]

    with download_progress['lock']:
        download_progress['total'] = len(to_download)
        download_progress['current'] = 0

    print(f"⬇️ Downloading {len(to_download)} resources...")

    # Use ThreadPoolExecutor for parallel downloads
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_resource = {
            executor.submit(download_single_resource, resource, headers): resource
            for resource in to_download
        }

        for future in as_completed(future_to_resource):
            resource = future_to_resource[future]
            try:
                success = future.result()
                with download_progress['lock']:
                    download_progress['current'] += 1
                    progress = (
                        download_progress['current'] / download_progress['total']) * 100
                    print(
                        f"📥 Progress: {progress:.1f}% - {resource['filename']}")
            except Exception as e:
                print(f"❌ Failed to download {resource['filename']}: {e}")
                resource['error'] = str(e)


def download_single_resource(resource, headers):
    """
    Download a single resource
    """
    try:
        response = requests.get(
            resource['url'], headers=headers, timeout=30, stream=True)
        response.raise_for_status()

        # Handle binary vs text content
        if is_binary_content(response.headers.get('content-type', '')):
            resource['content'] = base64.b64encode(
                response.content).decode('utf-8')
            resource['is_binary'] = True
        else:
            resource['content'] = response.text
            resource['is_binary'] = False

        resource['size'] = len(response.content)
        resource['downloaded'] = True
        resource['content_type'] = response.headers.get('content-type', '')

        return True

    except Exception as e:
        resource['error'] = str(e)
        resource['downloaded'] = False
        return False


def process_html_links(soup, resources, base_url):
    """
    Process HTML and update all links to point to local files
    """
    print("🔗 Processing HTML links...")

    # Create URL to local path mapping
    url_to_local = {}
    for resource in resources:
        if resource['url'] not in ['inline', 'data:embedded']:
            url_to_local[resource['url']] = resource['original_path']

    # Update CSS links
    for link in soup.find_all('link', href=True):
        href = link.get('href')
        full_url = urljoin(base_url, href)
        if full_url in url_to_local:
            link['href'] = url_to_local[full_url]

    # Update script sources
    for script in soup.find_all('script', src=True):
        src = script.get('src')
        full_url = urljoin(base_url, src)
        if full_url in url_to_local:
            script['src'] = url_to_local[full_url]

    # Update image sources
    for img in soup.find_all('img', src=True):
        src = img.get('src')
        full_url = urljoin(base_url, src)
        if full_url in url_to_local:
            img['src'] = url_to_local[full_url]

    # Update other attributes that might contain URLs
    for element in soup.find_all(attrs={'data-src': True}):
        data_src = element.get('data-src')
        full_url = urljoin(base_url, data_src)
        if full_url in url_to_local:
            element['data-src'] = url_to_local[full_url]

    return soup

# Helper functions


def clean_path(path):
    """Clean and normalize file paths"""
    if path.startswith('//'):
        path = 'https:' + path
    if path.startswith('http'):
        parsed = urlparse(path)
        path = parsed.path

    path = unquote(path).strip('/')

    # Remove query parameters and fragments
    if '?' in path:
        path = path.split('?')[0]
    if '#' in path:
        path = path.split('#')[0]

    # Ensure proper directory structure
    if '/' not in path and '.' in path:
        # It's a file in root, move to appropriate folder
        ext = path.split('.')[-1].lower()
        if ext in ['css']:
            path = f'css/{path}'
        elif ext in ['js']:
            path = f'js/{path}'
        elif ext in ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp']:
            path = f'images/{path}'
        elif ext in ['woff', 'woff2', 'ttf', 'eot']:
            path = f'fonts/{path}'

    return path or 'index.html'


def create_image_resource(src, base_url, alt=''):
    """Create an image resource object"""
    if src.startswith('data:'):
        # Handle data URLs
        data_match = re.match(r'data:image/([^;]+)', src)
        file_ext = data_match.group(1) if data_match else 'png'

        return {
            'filename': f'embedded-image.{file_ext}',
            'original_path': f'images/embedded-image.{file_ext}',
            'url': 'data:embedded',
            'content': src,
            'category': 'image',
            'type': 'embedded',
            'size': len(src),
            'downloaded': True,
            'alt': alt
        }
    else:
        full_url = urljoin(base_url, src)
        original_path = clean_path(src)

        return {
            'filename': os.path.basename(original_path),
            'original_path': original_path,
            'url': full_url,
            'content': '',
            'category': 'image',
            'type': 'external',
            'size': 0,
            'downloaded': False,
            'alt': alt
        }


def create_media_resource(src, base_url, media_type):
    """Create a media resource object"""
    full_url = urljoin(base_url, src)
    original_path = clean_path(src)

    return {
        'filename': os.path.basename(original_path),
        'original_path': original_path,
        'url': full_url,
        'content': '',
        'category': media_type,
        'type': 'external',
        'size': 0,
        'downloaded': False
    }


def parse_srcset(srcset):
    """Parse srcset attribute to extract URLs"""
    urls = []
    parts = srcset.split(',')
    for part in parts:
        url = part.strip().split()[0]
        if url:
            urls.append(url)
    return urls


def is_library_url(url):
    """Check if URL is a library/CDN"""
    cdn_patterns = [
        r'cdn\.jsdelivr\.net', r'cdnjs\.cloudflare\.com', r'unpkg\.com',
        r'ajax\.googleapis\.com', r'code\.jquery\.com', r'stackpath\.bootstrapcdn\.com',
        r'maxcdn\.bootstrapcdn\.com', r'use\.fontawesome\.com', r'fonts\.googleapis\.com'
    ]
    return any(re.search(pattern, url) for pattern in cdn_patterns)


def is_font_url(url):
    """Check if URL is a font file"""
    font_extensions = ['.woff', '.woff2', '.ttf', '.eot', '.otf']
    return any(url.lower().endswith(ext) for ext in font_extensions) or 'font' in url.lower()


def is_image_url(url):
    """Check if URL is an image file"""
    image_extensions = ['.png', '.jpg', '.jpeg',
                        '.gif', '.svg', '.webp', '.bmp', '.ico']
    return any(url.lower().endswith(ext) for ext in image_extensions)


def is_document_url(url):
    """Check if URL is a document file"""
    doc_extensions = ['.pdf', '.doc', '.docx', '.xls',
                      '.xlsx', '.ppt', '.pptx', '.zip', '.rar']
    return any(url.lower().endswith(ext) for ext in doc_extensions)


def is_binary_content(content_type):
    """Check if content type is binary"""
    text_types = ['text/', 'application/json',
                  'application/xml', 'application/javascript']
    return not any(text_type in content_type.lower() for text_type in text_types)
