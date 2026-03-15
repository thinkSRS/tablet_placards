#!/usr/bin/env python3
"""
SRS Product Display Generator
Renders HTML from Jinja2 template using CSV product data
"""

import csv
import re
from jinja2 import Template


def resolve_product_urls(product):
    """
    Resolve URL fields with the following fallback priority:
      1. Full URL specified in the field → use as-is
      2. Bracketed part number, e.g. [LDC500] → build default URL using that PN
      3. Blank field → build default URL using product_pn
    Default URL patterns:
      datasheet_link:   https://www.thinksrs.com/downloads/pdfs/catalog/{PN}c.pdf
      manual_link:      https://www.thinksrs.com/downloads/pdfs/manuals/{PN}m.pdf
      product_page_url: https://www.thinksrs.com/products/{pn_lower}.html
    """
    pn = product.get('product_pn', '')

    def resolve(field_value, url_fn):
        value = (field_value or '').strip()
        if not value:
            if not pn:
                print(f"Warning: product_pn is empty and no URL provided; link will be blank.")
                return ''
            return url_fn(pn)
        m = re.fullmatch(r'\[([^\]]+)\]', value)
        if m:
            return url_fn(m.group(1))
        return value

    product['datasheet_link'] = resolve(
        product.get('datasheet_link', ''),
        lambda p: f'https://www.thinksrs.com/downloads/pdfs/catalog/{p}c.pdf',
    )
    product['manual_link'] = resolve(
        product.get('manual_link', ''),
        lambda p: f'https://www.thinksrs.com/downloads/pdfs/manuals/{p}m.pdf',
    )
    product['product_page_url'] = resolve(
        product.get('product_page_url', ''),
        lambda p: f'https://www.thinksrs.com/products/{p.lower()}.html',
    )
    return product

def load_products(csv_file):
    """Load product data from CSV file"""
    products = []
    
    # Try different encodings
    encodings_to_try = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
    
    for encoding in encodings_to_try:
        try:
            with open(csv_file, 'r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                products = list(reader)
                
                if products:
                    # Show what columns we found
                    print(f"Successfully read CSV with {encoding} encoding")
                    print(f"Found columns: {list(products[0].keys())}")
                    return products
        except Exception as e:
            continue
    
    raise Exception(f"Could not read CSV file with any standard encoding")

def render_template(template_file, products, categories):
    """Render Jinja2 template with product data"""
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    template = Template(template_content)
    return template.render(products=products, categories=categories)

def main():
    # Load product data from CSV
    try:
        products = load_products('products.csv')
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return
    
    # Resolve URL fields with default fallbacks
    products = [resolve_product_urls(p) for p in products]

    # Sort products by category, then by product_pn
    products.sort(key=lambda x: (x.get('category', ''), x.get('product_pn', '')))
    
    # Extract unique categories in order
    categories = []
    seen = set()
    for product in products:
        cat = product.get('category', '')
        if cat and cat not in seen:
            categories.append(cat)
            seen.add(cat)
    
    # Render template
    html_output = render_template('template.html', products, categories)
    
    # Write output HTML
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print(f"\nGenerated index.html with {len(products)} products")
    print(f"Categories: {', '.join(categories)}")
    print("\nProducts included:")
    for product in products:
        print(f"  - {product['product_pn']}: {product['product_name']} ({product.get('category', 'N/A')})")

if __name__ == '__main__':
    main()
