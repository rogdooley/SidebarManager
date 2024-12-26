import argparse
import os
from Cocoa import NSURL
from CoreFoundation import CFPreferencesAppSynchronize
from LaunchServices import (
    LSSharedFileListCreate,
    LSSharedFileListCopySnapshot,
    LSSharedFileListItemCopyDisplayName,
    LSSharedFileListItemCopyResolvedURL,
    LSSharedFileListItemRemove,
    LSSharedFileListInsertItemURL,
    kLSSharedFileListFavoriteItems,
    kLSSharedFileListItemBeforeFirst,
)


class FinderSidebarManager:
    """A class to manage Finder sidebar favorites."""

    def __init__(self):
        self.sfl_ref = LSSharedFileListCreate(
            None, kLSSharedFileListFavoriteItems, None
        )
        self.snapshot = None
        self.favorites = {}
        self.update()

    def update(self):
        """Update the snapshot and favorites."""
        self.snapshot = LSSharedFileListCopySnapshot(self.sfl_ref, None)
        self.favorites = {}
        for item in self.snapshot[0]:
            name = LSSharedFileListItemCopyDisplayName(item)
            url_ref = LSSharedFileListItemCopyResolvedURL(item, 0, None)
            if name and url_ref:
                self.favorites[name] = item

    def export_favorites(self, file_path):
        """Export the sidebar favorites to a file."""
        with open(file_path, "w") as file:
            for name, path in self.favorites.items():
                resolved_url = LSSharedFileListItemCopyResolvedURL(
                    self.favorites[name], 0, None
                )[0]
                file.write(f"{name} -> {resolved_url}\n")
        print(f"Favorites exported to {file_path}")

    def import_favorites(self, file_path):
        """Import sidebar favorites from a file.
        
        The file should contain entries in the format:
        'label -> url'
        For example:
        'Dropbox -> file:///Users/username/Dropbox/'
        ' -> nwnode://domain-AirDrop'
        """
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return

        # First remove all existing favorites
        self.remove_all()
        
        # Read and parse the file
        with open(file_path, 'r') as file:
            previous_label = None
            for line in file:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Split on ' -> ' to handle cases where label might contain '->'
                    parts = line.split(' -> ', 1)
                    if len(parts) != 2:
                        print(f"Warning: Skipping invalid line format: {line}")
                        continue
                        
                    label, url = parts
                    label = label.strip()
                    url = url.strip()
                    
                    # Add the favorite after the previous one
                    self.add(label, url, after=previous_label)
                    previous_label = label
                    
                except Exception as e:
                    print(f"Error processing line '{line}': {str(e)}")
                    continue
        
        print(f"Favorites imported from {file_path}")

    def add(self, label, path, after=None):
        """Add a new favorite, optionally after another favorite."""
        item_url = NSURL.URLWithString_(path)

        # Find the "after" item reference if specified
        after_item = self.favorites.get(after) if after else kLSSharedFileListItemBeforeFirst

        LSSharedFileListInsertItemURL(
            self.sfl_ref, after_item, label, None, item_url, None, None
        )
        CFPreferencesAppSynchronize("com.apple.sidebarlists")
        print(f"Added: {label} -> {path} after {after if after else 'start'}")
        self.update()

    def remove(self, label):
        """Remove a favorite by label."""
        if label in self.favorites:
            LSSharedFileListItemRemove(self.sfl_ref, self.favorites[label])
            CFPreferencesAppSynchronize("com.apple.sidebarlists")
            print(f"Removed: {label}")
            self.update()
        else:
            print(f"Error: Favorite '{label}' not found.")

    def remove_all(self):
        """Remove all sidebar favorites."""
        for item in self.favorites.values():
            LSSharedFileListItemRemove(self.sfl_ref, item)
        CFPreferencesAppSynchronize("com.apple.sidebarlists")
        print("All favorites removed.")
        self.update()


def main():
    parser = argparse.ArgumentParser(description="Manage Finder Sidebar Favorites")
    parser.add_argument("-f", "--file", type=str, help="File path for import/export")
    parser.add_argument("-e", "--export", action="store_true", help="Export favorites")
    parser.add_argument(
        "-i", "--import-file", action="store_true", help="Import favorites"
    )
    parser.add_argument(
        "-a",
        "--add",
        nargs=2,
        metavar=("LABEL", "PATH"),
        help="Add a favorite",
    )
    parser.add_argument(
        "-A",
        "--add-after",
        nargs=3,
        metavar=("LABEL", "PATH", "AFTER"),
        help="Add a favorite after another",
    )
    parser.add_argument("-r", "--remove", metavar="LABEL", help="Remove a favorite")

    args = parser.parse_args()
    manager = FinderSidebarManager()

    if args.export and args.file:
        manager.export_favorites(args.file)
    elif args.import_file and args.file:
        manager.import_favorites(args.file)
    elif args.add:
        label, path = args.add
        manager.add(label, path)
    elif args.add_after:
        label, path, after = args.add_after
        manager.add(label, path, after)
    elif args.remove:
        manager.remove(args.remove)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
