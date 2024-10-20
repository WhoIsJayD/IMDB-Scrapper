import os

def print_directory_structure(path, indent=0):
    # Iterate through all the items in the directory
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        # Print the current item with indentation
        print(' ' * indent + item)
        if os.path.isdir(item_path):
            # If the item is a directory, recursively print its structure
            print_directory_structure(item_path, indent + 4)

# Get the current working directory
current_directory = os.getcwd()
print_directory_structure(current_directory)
