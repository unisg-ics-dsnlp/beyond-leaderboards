"""
Profile Loader for Structured Knowledge Layer

Simple, focused class to load and manage worldview profiles.
"""

import json
import glob
import os
from pathlib import Path
from typing import Dict, List, Any


class ProfileLoader:
    """Loads and manages ideological profiles from JSON files"""

    def __init__(self, profiles_dir: str | Path):
        self.profiles_dir = profiles_dir
        self.profiles = {}
        self.load_profiles()

    def load_profiles(self):
        """Load all JSON profiles from the profiles directory"""
        profile_pattern = os.path.join(self.profiles_dir, "*.json")

        for profile_path in glob.glob(profile_pattern):
            try:
                with open(profile_path, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)

                worldview_id = profile_data.get('worldview_id')
                if worldview_id:
                    self.profiles[worldview_id] = profile_data

            except Exception as e:
                print(f"✗ Error loading {profile_path}: {e}")

    def get_profile(self, worldview_id: str) -> Dict[str, Any]:
        """Get a specific profile by ID"""
        # If profile not found, try reloading profiles (in case new profiles were added)
        if worldview_id not in self.profiles:
            self.load_profiles()
        return self.profiles.get(worldview_id)

    def list_profiles(self) -> List[str]:
        """List all available profile IDs"""
        return list(self.profiles.keys())

    def get_profile_summary(self, worldview_id: str) -> str:
        """Generate a summary of a profile for reasoning"""
        profile = self.get_profile(worldview_id)
        if not profile:
            return ""

        summary = f"""
Worldview: {profile.get('display_name', worldview_id)}

Core Values:
{self._format_weighted_items(profile.get('core_values', []))}

Key Definitions:
{self._format_definitions(profile.get('key_definitions', []))}

Assumed Principles:
{self._format_weighted_items(profile.get('assumed_principles', []), 'priority')}
        """.strip()

        return summary

    def _format_weighted_items(self, items: List[Dict], weight_key: str = 'weight') -> str:
        """Format weighted items for display"""
        formatted = []
        for item in items:
            weight = item.get(weight_key, 0)
            name = item.get('name', 'Unknown')
            desc = item.get('desc', '')
            formatted.append(f"• {name} ({weight:.2f}): {desc}")
        return '\n'.join(formatted)

    def _format_definitions(self, definitions: List[Dict]) -> str:
        """Format definitions for display"""
        formatted = []
        for defn in definitions:
            term = defn.get('term', 'Unknown')
            definition = defn.get('definition', '')
            formatted.append(f"• {term}: {definition}")
        return '\n'.join(formatted)
