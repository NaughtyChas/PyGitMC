import os
import json

class SaveManager:
    
    def __init__(self):
        self.saves = {}  # {save_name: save_path}
        self.current_save = None
        
    def add_save(self, directory):
        """Add a save to the list"""
        if not os.path.exists(directory) or not os.path.isdir(directory):
            return False, "Invalid directory"
        
        save_name = os.path.basename(directory)
        
        # Check if it's already in the list
        if save_name in self.saves:
            return True, "Save already exists"
        
        # Add to saves dictionary
        self.saves[save_name] = directory
        self.current_save = save_name
        
        return True, f"Added save: {save_name}"
    
    def remove_save(self, save_name):
        """Remove a save from the list"""
        if save_name in self.saves:
            del self.saves[save_name]
            
            # Reset current save if it was removed
            if self.current_save == save_name:
                self.current_save = None
            
            return True, f"Removed save: {save_name}"
        
        return False, "Save not found"
    
    def get_save_path(self, save_name):
        """Get the path of a save"""
        return self.saves.get(save_name)
    
    def set_current_save(self, save_name):
        """Set the current save"""
        if save_name in self.saves:
            self.current_save = save_name
            return True
        return False
    
    def get_current_save(self):
        """Get the current save"""
        if self.current_save:
            return self.current_save, self.saves[self.current_save]
        return None, ""
    
    def get_all_saves(self):
        """Get all saves"""
        return self.saves
    
    def save_config(self, config_path="saves_config.json"):
        """Save the current configuration to a file"""
        try:
            config = {
                "saves": self.saves,
                "current_save": self.current_save
            }
            
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            
            return True, "Configuration saved successfully"
        except Exception as e:
            return False, f"Failed to save configuration: {str(e)}"
    
    def load_config(self, config_path="saves_config.json"):
        """Load the configuration from a file"""
        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)
                
                self.saves = config.get("saves", {})
                self.current_save = config.get("current_save")
                
                return True, "Configuration loaded successfully"
            
            return False, "Configuration file not found"
        except Exception as e:
            return False, f"Failed to load configuration: {str(e)}"
    
    def get_save_info(self, save_name):
        """Get information about a save"""
        path = self.get_save_path(save_name)
        if not path:
            return None
            
        # Add more logic to get more information about the save
        # For instance last modified date, last commit message, etc.
        last_modified = None
        try:
            last_modified = os.path.getmtime(path)
            last_modified = "Today at 14:32"  # Translate to human-readable format
        except:
            last_modified = "Unknown"
            
        return {
            "name": save_name,
            "path": path,
            "last_modified": last_modified,
            "last_commit": "Added new farm area (12 hours ago)"  # Get message from git
        }