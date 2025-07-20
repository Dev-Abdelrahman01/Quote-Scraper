#!/usr/bin/env python3
"""
QuoteScraper - Professional Web Scraping Tool
A beginner-friendly Python project demonstrating:
- Web scraping with requests and BeautifulSoup
- HTML parsing and data extraction
- Data storage in multiple formats (CSV, JSON)
- Error handling and robust web interactions
- Professional data collection workflows
"""

import requests
from bs4 import BeautifulSoup
import csv
import json
import time
from datetime import datetime
import os

def display_banner():
    """Display the application banner."""
    print("=" * 60)
    print("           QUOTESCRAPER")
    print("     Professional Web Scraping Tool")
    print("=" * 60)
    print()

def get_quotes_from_page(url, session):
    """Extract quotes from a single page."""
    try:
        print(f"📡 Fetching data from: {url}")
        
        # Add headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all quote containers
        quote_containers = soup.find_all('div', class_='quote')
        
        quotes_data = []
        
        for container in quote_containers:
            try:
                # Extract quote text
                quote_text = container.find('span', class_='text')
                if quote_text:
                    quote_text = quote_text.get_text(strip=True)
                else:
                    continue
                
                # Extract author
                author = container.find('small', class_='author')
                if author:
                    author = author.get_text(strip=True)
                else:
                    author = "Unknown"
                
                # Extract tags
                tag_elements = container.find_all('a', class_='tag')
                tags = [tag.get_text(strip=True) for tag in tag_elements]
                
                quote_data = {
                    'text': quote_text,
                    'author': author,
                    'tags': tags,
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                quotes_data.append(quote_data)
                
            except Exception as e:
                print(f"⚠️  Error processing individual quote: {e}")
                continue
        
        print(f"✓ Successfully extracted {len(quotes_data)} quotes from this page")
        return quotes_data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return []
    except Exception as e:
        print(f"❌ Error parsing page: {e}")
        return []

def get_next_page_url(soup, base_url):
    """Find the URL of the next page."""
    try:
        next_link = soup.find('li', class_='next')
        if next_link:
            next_href = next_link.find('a')['href']
            return base_url + next_href
        return None
    except:
        return None

def scrape_all_quotes(base_url="http://quotes.toscrape.com", max_pages=10):
    """Scrape quotes from multiple pages."""
    all_quotes = []
    current_url = base_url
    page_count = 0
    
    # Create a session for connection reuse
    session = requests.Session()
    
    print(f"🚀 Starting to scrape quotes from {base_url}")
    print(f"📄 Maximum pages to scrape: {max_pages}")
    print()
    
    while current_url and page_count < max_pages:
        page_count += 1
        print(f"📖 Scraping page {page_count}...")
        
        # Get quotes from current page
        page_quotes = get_quotes_from_page(current_url, session)
        all_quotes.extend(page_quotes)
        
        # Get the next page URL
        try:
            response = session.get(current_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            current_url = get_next_page_url(soup, base_url)
        except:
            current_url = None
        
        # Be respectful to the server
        time.sleep(1)
        
        if not current_url:
            print("📄 No more pages found.")
            break
    
    print(f"\n🎉 Scraping completed!")
    print(f"📊 Total quotes collected: {len(all_quotes)}")
    print(f"📄 Pages scraped: {page_count}")
    
    return all_quotes

def save_to_csv(quotes, filename="quotes.csv"):
    """Save quotes to a CSV file."""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['text', 'author', 'tags', 'scraped_at']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for quote in quotes:
                # Convert tags list to string for CSV
                quote_copy = quote.copy()
                quote_copy['tags'] = ', '.join(quote['tags'])
                writer.writerow(quote_copy)
        
        print(f"✓ CSV file saved: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving CSV: {e}")
        return False

def save_to_json(quotes, filename="quotes.json"):
    """Save quotes to a JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(quotes, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"✓ JSON file saved: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving JSON: {e}")
        return False

def analyze_quotes(quotes):
    """Perform basic analysis on the scraped quotes."""
    if not quotes:
        print("No quotes to analyze.")
        return
    
    print(f"\n{'='*60}")
    print("QUOTE ANALYSIS")
    print(f"{'='*60}")
    
    # Basic statistics
    total_quotes = len(quotes)
    print(f"📊 Total quotes: {total_quotes}")
    
    # Author analysis
    authors = {}
    for quote in quotes:
        author = quote['author']
        authors[author] = authors.get(author, 0) + 1
    
    print(f"👥 Unique authors: {len(authors)}")
    print(f"🏆 Most quoted author: {max(authors, key=authors.get)} ({authors[max(authors, key=authors.get)]} quotes)")
    
    # Tag analysis
    all_tags = []
    for quote in quotes:
        all_tags.extend(quote['tags'])
    
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    print(f"🏷️  Total tags: {len(all_tags)}")
    print(f"🔖 Unique tags: {len(tag_counts)}")
    
    if tag_counts:
        most_common_tag = max(tag_counts, key=tag_counts.get)
        print(f"🎯 Most common tag: '{most_common_tag}' ({tag_counts[most_common_tag]} times)")
    
    # Quote length analysis
    quote_lengths = [len(quote['text']) for quote in quotes]
    avg_length = sum(quote_lengths) / len(quote_lengths)
    print(f"📏 Average quote length: {avg_length:.1f} characters")
    print(f"📏 Shortest quote: {min(quote_lengths)} characters")
    print(f"📏 Longest quote: {max(quote_lengths)} characters")
    
    # Top authors
    print(f"\n🏆 TOP 5 AUTHORS:")
    sorted_authors = sorted(authors.items(), key=lambda x: x[1], reverse=True)
    for i, (author, count) in enumerate(sorted_authors[:5], 1):
        print(f"  {i}. {author}: {count} quotes")
    
    # Top tags
    if tag_counts:
        print(f"\n🔖 TOP 10 TAGS:")
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        for i, (tag, count) in enumerate(sorted_tags[:10], 1):
            print(f"  {i}. {tag}: {count} times")

def display_sample_quotes(quotes, count=5):
    """Display a sample of scraped quotes."""
    if not quotes:
        print("No quotes to display.")
        return
    
    print(f"\n{'='*60}")
    print(f"SAMPLE QUOTES (showing {min(count, len(quotes))} of {len(quotes)})")
    print(f"{'='*60}")
    
    for i, quote in enumerate(quotes[:count], 1):
        print(f"\n📝 Quote {i}:")
        print(f"   \"{quote['text']}\"")
        print(f"   — {quote['author']}")
        if quote['tags']:
            print(f"   🏷️  Tags: {', '.join(quote['tags'])}")
        print(f"   ⏰ Scraped: {quote['scraped_at']}")

def search_quotes(quotes, search_term):
    """Search for quotes containing a specific term."""
    if not quotes:
        print("No quotes to search.")
        return []
    
    search_term = search_term.lower()
    matching_quotes = []
    
    for quote in quotes:
        if (search_term in quote['text'].lower() or 
            search_term in quote['author'].lower() or 
            any(search_term in tag.lower() for tag in quote['tags'])):
            matching_quotes.append(quote)
    
    print(f"\n🔍 Found {len(matching_quotes)} quotes matching '{search_term}':")
    
    for i, quote in enumerate(matching_quotes[:5], 1):  # Show first 5 matches
        print(f"\n{i}. \"{quote['text']}\" — {quote['author']}")
        if quote['tags']:
            print(f"   Tags: {', '.join(quote['tags'])}")
    
    if len(matching_quotes) > 5:
        print(f"\n... and {len(matching_quotes) - 5} more matches.")
    
    return matching_quotes

def display_menu():
    """Display the main menu."""
    print(f"\n{'='*60}")
    print("MAIN MENU")
    print(f"{'='*60}")
    print("1. 🕷️  Scrape quotes from website")
    print("2. 📊 Analyze scraped data")
    print("3. 📝 Display sample quotes")
    print("4. 🔍 Search quotes")
    print("5. 💾 Save data to files")
    print("6. 📁 Load data from file")
    print("7. Exit")
    print()

def get_user_choice():
    """Get the user's menu choice."""
    while True:
        try:
            choice = int(input("Enter your choice (1-7): "))
            if 1 <= choice <= 7:
                return choice
            else:
                print("Please enter a number between 1 and 7.")
        except ValueError:
            print("Please enter a valid number.")

def get_scraping_parameters():
    """Get scraping parameters from user."""
    print("\n📋 Scraping Configuration:")
    
    # Get maximum pages
    while True:
        try:
            max_pages = int(input("Enter maximum pages to scrape (1-20, default 5): ") or "5")
            if 1 <= max_pages <= 20:
                break
            else:
                print("Please enter a number between 1 and 20.")
        except ValueError:
            print("Please enter a valid number.")
    
    return max_pages

def load_quotes_from_file(filename="quotes.json"):
    """Load quotes from a JSON file."""
    try:
        if not os.path.exists(filename):
            print(f"❌ File '{filename}' not found.")
            return []
        
        with open(filename, 'r', encoding='utf-8') as file:
            quotes = json.load(file)
        
        print(f"✓ Loaded {len(quotes)} quotes from {filename}")
        return quotes
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return []

def main():
    """Main application entry point."""
    display_banner()
    print("Welcome to QuoteScraper!")
    print("A professional tool for collecting inspirational quotes from the web.")
    
    quotes_data = []
    
    try:
        while True:
            display_menu()
            choice = get_user_choice()
            
            if choice == 7:
                print("\nThank you for using QuoteScraper!")
                print("Keep collecting inspiration! 📚")
                break
            
            elif choice == 1:
                print(f"\n{'='*60}")
                print("WEB SCRAPING")
                print(f"{'='*60}")
                
                max_pages = get_scraping_parameters()
                quotes_data = scrape_all_quotes(max_pages=max_pages)
                
                if quotes_data:
                    print(f"\n✅ Successfully scraped {len(quotes_data)} quotes!")
                else:
                    print("\n❌ No quotes were scraped. Please check your internet connection.")
            
            elif choice == 2:
                if quotes_data:
                    analyze_quotes(quotes_data)
                else:
                    print("\n⚠️  No data to analyze. Please scrape quotes first or load from file.")
            
            elif choice == 3:
                if quotes_data:
                    count = int(input("\nHow many quotes to display (default 5): ") or "5")
                    display_sample_quotes(quotes_data, count)
                else:
                    print("\n⚠️  No quotes available. Please scrape quotes first or load from file.")
            
            elif choice == 4:
                if quotes_data:
                    search_term = input("\nEnter search term: ").strip()
                    if search_term:
                        search_quotes(quotes_data, search_term)
                    else:
                        print("Please enter a valid search term.")
                else:
                    print("\n⚠️  No quotes available. Please scrape quotes first or load from file.")
            
            elif choice == 5:
                if quotes_data:
                    print(f"\n{'='*60}")
                    print("SAVING DATA")
                    print(f"{'='*60}")
                    
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    csv_filename = f"quotes_{timestamp}.csv"
                    json_filename = f"quotes_{timestamp}.json"
                    
                    save_to_csv(quotes_data, csv_filename)
                    save_to_json(quotes_data, json_filename)
                    
                    print(f"\n📁 Files saved in current directory:")
                    print(f"   • {csv_filename}")
                    print(f"   • {json_filename}")
                else:
                    print("\n⚠️  No data to save. Please scrape quotes first.")
            
            elif choice == 6:
                filename = input("\nEnter filename to load (default: quotes.json): ").strip() or "quotes.json"
                loaded_quotes = load_quotes_from_file(filename)
                if loaded_quotes:
                    quotes_data = loaded_quotes
            
            if choice != 7:
                input("\nPress Enter to continue...")
    
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye! 👋")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("Please restart the program.")

if __name__ == "__main__":
    main()

