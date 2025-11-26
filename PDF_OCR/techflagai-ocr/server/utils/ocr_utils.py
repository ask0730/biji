import os

def format_items_as_markdown_table(items_list):
    """
    Formats a list of OCR items (with row/col info) into a Markdown table string.
    Assumes items_list is a list of dicts like:
    {"box": [...], "col": [start_col, end_col], "row": [start_row, end_row], "text": "...", ...}
    """
    if not items_list:
        return ""

    # Find max row and column indices
    max_row = 0
    max_col = 0
    for item in items_list:
        # Use end_row and end_col to determine table dimensions
        max_row = max(max_row, item.get('row', [0, 0])[1])
        max_col = max(max_col, item.get('col', [0, 0])[1])

    # Create a 2D list to hold table data, initialized with empty strings
    # Dimensions are (max_row + 1) x (max_col + 1)
    table_data = [["" for _ in range(max_col + 1)] for _ in range(max_row + 1)]

    # Populate the table data
    for item in items_list:
        row_start = item.get('row', [0, 0])[0]
        col_start = item.get('col', [0, 0])[0]
        text = item.get('text', "")

        # Place text in the top-left cell of the item's span
        # Ensure indices are within bounds
        if 0 <= row_start <= max_row and 0 <= col_start <= max_col:
            # Escape pipes in text to avoid breaking markdown table format
            escaped_text = text.replace('|', '\\|')
            table_data[row_start][col_start] = escaped_text

    # Generate Markdown table string
    markdown_lines = []

    # Header row
    header = "| " + " | ".join([f"Col {i}" for i in range(max_col + 1)]) + " |"
    markdown_lines.append(header)

    # Separator row
    separator = "|-" + "-|-".join(['-------' for _ in range(max_col + 1)]) + "|"
    markdown_lines.append(separator)

    # Data rows
    for row_data in table_data:
        row_string = "| " + " | ".join(row_data) + " |"
        markdown_lines.append(row_string)

    return "\n".join(markdown_lines)

# Example Usage (for testing)
# if __name__ == "__main__":
#     sample_items = [
#         {"row": [0, 0], "col": [0, 0], "text": "Header 1"},
#         {"row": [0, 0], "col": [1, 1], "text": "Header 2"},
#         {"row": [1, 1], "col": [0, 0], "text": "Data A"},
#         {"row": [1, 1], "col": [1, 1], "text": "Data B"},
#         {"row": [2, 2], "col": [0, 1], "text": "Spanning Cell | with pipe"} # Example of spanning and pipe
#     ]
#     markdown_table = format_items_as_markdown_table(sample_items)
#     print(markdown_table)

#     sample_items_single = [
#         {
#             "box": [1222, 220, 1542, 220],
#             "col": [0, 0],
#             "position": [1222, 220, 1542, 220, 1542, 280, 1222, 280],
#             "row": [0, 0],
#             "score": 0.999,
#             "text": "玻璃纤维空气过滤",
#             "type": "text"
#         }
#     ]
#     markdown_table_single = format_items_as_markdown_table(sample_items_single)
#     print("\n--- Single Item Example ---")
#     print(markdown_table_single)