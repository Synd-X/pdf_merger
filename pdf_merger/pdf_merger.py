import os
import re
import argparse
from pathlib import Path

from PyPDF2 import PdfMerger


def list_pdf_files(input_folder):
    """Returns a list of PDF files in the given folder."""
    return [f for f in os.listdir(input_folder) if f.endswith('.pdf')]


def extract_index_from_filename(filename, prefix, index_pattern):
    """Removes the prefix from the filename and extracts the index using the regex pattern."""
    clean_name = filename[len(prefix):] if filename.startswith(prefix) else filename
    match = re.search(index_pattern, clean_name)
    return int(match.group(1)) if match else None


def get_sorted_pdfs_by_index(pdf_files, prefix, index_pattern):
    """Returns a list of (filename, index) tuples sorted by index."""
    pdf_with_indices = {}
    for pdf_file in pdf_files:
        index = extract_index_from_filename(pdf_file, prefix, index_pattern)
        if index is not None:
            pdf_with_indices[pdf_file] = index
        else:
            print(f"Warning: No index found for file {pdf_file}. Skipping.")
    return sorted(pdf_with_indices.items(), key=lambda x: x[1])


def get_sorted_pdfs_by_order(pdf_files, custom_order):
    """Sorts PDF files based on a custom user-defined order."""
    if len(pdf_files) != len(custom_order):
        raise ValueError("The number of files does not match the number of custom order positions.")

    # Create a dictionary with files and corresponding order
    pdf_with_order = {pdf_file: order for pdf_file, order in zip(pdf_files, custom_order)}
    return sorted(pdf_with_order.items(), key=lambda x: x[1])


def confirm_merge(sorted_pdfs):
    """Displays the sorted PDF list and requests confirmation to proceed with merging."""
    print("\nThe following PDFs will be merged in this order:")
    for pdf_file, order_or_index in sorted_pdfs:
        print(f"{pdf_file} (Order/Index: {order_or_index})")

    return input("\nDo you want to proceed with merging these files? (yes/no): ").strip().lower() == 'yes'

def merge_pdfs(input_folder, output_file, sorted_pdfs, custom_titles=None):
    """Merges the sorted PDFs into the output file and adds bookmarks as a Table of Contents."""
    merger = PdfMerger()
    current_page = 0  # To track the current page number for bookmarks

    for idx, (pdf_file, _) in enumerate(sorted_pdfs):
        # Convert to a Path object
        pdf_path = Path(input_folder) / pdf_file

        # Append the PDF file
        merger.append(str(pdf_path))  # Ensure it's passed as a string

        # Add a bookmark for the beginning of this PDF file
        bookmark_title = custom_titles[idx] if custom_titles and idx < len(custom_titles) else pdf_path.stem
        merger.add_outline_item(bookmark_title, current_page)
        print(f"Adding {pdf_file} to the merged PDF with bookmark title: '{bookmark_title}'.")

        # Update the current page number after adding the file
        current_page += merger.pages[-1].numPages  # Get the number of pages in the last added file

    # Write the merged output to the output file
    with open(output_file, 'wb') as f_out:
        merger.write(f_out)
        print(f"Merged PDF saved as {output_file} with Table of Contents (Bookmarks).")

    # Close the merger
    merger.close()


def parse_custom_order(order_str):
    """Parses a comma-separated string of order into a list of integers."""
    return [int(order) for order in order_str.split(',')]


def main():
    """Main function to handle argument parsing and workflow."""
    parser = argparse.ArgumentParser(
        description="Merge multiple PDF files into one, after removing a prefix and sorting by an index in the filename."
    )

    parser.add_argument(
        '-i', '--input_folder',
        required=True,
        help="Path to the folder containing the PDF files to merge."
    )
    parser.add_argument(
        '-o', '--output_file',
        required=True,
        help="The path where the merged PDF will be saved."
    )
    parser.add_argument(
        '-p', '--prefix',
        default='',
        help="Prefix to be removed from filenames before sorting. Default is an empty string."
    )
    parser.add_argument(
        '-r', '--index_pattern',
        default=r'(\d+)',
        help="Regex pattern to capture the index from filenames after removing the prefix. Default is a number pattern."
    )
    parser.add_argument(
        '--custom_titles',
        help="Comma-separated list of custom titles for the Table of Contents (bookmarks). Example: 'Title1,Title2,Title3'."
    )
    parser.add_argument(
        '--custom_order',
        help="Comma-separated list of custom order indices. Example: '1,2,3'. This overrides index-based sorting."
    )
    parser.add_argument(
        '--force_merge',
        action='store_true',
        help="If set, the program will merge the PDFs without asking for confirmation."
    )

    args = parser.parse_args()

    # Step 1: List PDF files
    pdf_files = list_pdf_files(args.input_folder)

    if not pdf_files:
        print(f"No PDF files found in the directory: {args.input_folder}")
        return

    # Step 2: Sort PDFs by index or by user-specified order
    if args.custom_order:
        custom_order = parse_custom_order(args.custom_order)
        sorted_pdfs = get_sorted_pdfs_by_order(pdf_files, custom_order)
    else:
        sorted_pdfs = get_sorted_pdfs_by_index(pdf_files, args.prefix, args.index_pattern)

    if not sorted_pdfs:
        print("No valid PDFs with index found. Exiting.")
        return

    # Step 3: Get custom titles if provided
    custom_titles = args.custom_titles.split(',') if args.custom_titles else None

    # Step 4: Request user confirmation unless forced to merge
    if not args.force_merge and not confirm_merge(sorted_pdfs):
        print("Merge operation aborted by the user.")
        return

    # Step 5: Merge PDFs with Table of Contents (Bookmarks)
    merge_pdfs(args.input_folder, args.output_file, sorted_pdfs, custom_titles)


if __name__ == '__main__':
    main()
