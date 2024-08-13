import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def sanitize_filename(filename):
    """Sanitize the filename by removing invalid characters."""
    return re.sub(r'[^\w\s-]', '', filename).strip().replace(' ', '_')

def sanitize_text(text):
    """Sanitize text by removing citations or footnotes."""
    return re.sub(r'\[\d+\]', '', text).strip()

def extract_tables_from_url(url, output_folder='output_tables'):
    """Extract tables from a URL and save or append them as CSV files."""
    # Fetch the page content
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    
    # Find all tables on the page
    tables = soup.find_all('table')
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Track processed tables to avoid duplicates
    seen_tables = set()
    
    for i, table in enumerate(tables):
        # Convert table to string and check if it's already processed
        table_str = str(table)
        if table_str in seen_tables:
            continue
        seen_tables.add(table_str)
        
        # Extract the table title or closest heading (h2, h3) or the first header
        table_title_tag = table.find_previous(['h2', 'h3']) or table.find('th')
        table_title = table_title_tag.text.strip() if table_title_tag else f'Table_{i+1}'
        
        # Sanitize the filename
        csv_filename = sanitize_filename(table_title) + '.csv'
        csv_path = os.path.join(output_folder, csv_filename)
        
        # Extract table headers
        headers = []
        unnamed_count = 1
        for header in table.find_all('th'):
            header_text = header.text.strip()
            if not header_text:
                header_text = f'unnamed_column_{unnamed_count}'
                unnamed_count += 1
            headers.append(header_text)
        
        # Create a DataFrame with the headers
        df = pd.DataFrame(columns=headers)
        
        # Detect columns with non-useful data
        non_useful_columns = set()
        
        # Extract table rows
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip the header row
            cells = row.find_all('td')
            cell_data = []
            for j, cell in enumerate(cells):
                # Handle images within cells by replacing them with "null"
                if cell.find('img'):
                    non_useful_columns.add(j)
                    cell_data.append('null')
                    continue
                
                # Remove links but keep the text
                for link in cell.find_all('a'):
                    link_text = link.text.strip()
                    link.extract()
                    cell.append(link_text)

                # Extract text from the cell
                cell_text = ' '.join(cell.stripped_strings) or 'null'
                cell_text = sanitize_text(cell_text)
                cell_data.append(cell_text)
            
            # Adjust cell_data to match the number of headers
            if len(cell_data) < len(df.columns):
                cell_data.extend([''] * (len(df.columns) - len(cell_data)))
            elif len(cell_data) > len(df.columns):
                additional_headers = [f'Extra_{j+1}' for j in range(len(cell_data) - len(df.columns))]
                df = df.reindex(columns=df.columns.tolist() + additional_headers)
                print(f"Added additional headers: {additional_headers}")
                df = df.fillna('')
            
            # Insert the row into the DataFrame
            df.loc[len(df)] = cell_data
        
        # Replace non-useful columns with 'null' or '0'
        for col_index in non_useful_columns:
            df.iloc[:, col_index] = 'null'
        
        # Check if the CSV file already exists
        if os.path.exists(csv_path):
            existing_df = pd.read_csv(csv_path)
            if list(df.columns) == list(existing_df.columns):
                df.to_csv(csv_path, mode='a', header=False, index=False)
                print(f"Appended to {csv_filename}.")
            else:
                print(f"Columns do not match for {csv_filename}. New table will not be appended.")
        else:
            df.to_csv(csv_path, index=False)
            print(f"Saved {csv_filename}.")
    
    print("All tables have been extracted and saved as CSV files.")

# Example usage
url = 'https://ceoworld.biz/2024/02/13/egypts-largest-companies-by-market-capitalization-2024/'
extract_tables_from_url(url)
