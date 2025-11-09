"""Local file storage for analysis results."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from config import ANALYSES_DIR
from exceptions import StorageWriteError, StorageReadError
from logger import get_logger

logger = get_logger(__name__)


class StorageManager:
    """Manages persistent storage of analyses in ~/.janus-clew/"""

    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize storage manager.

        Args:
            base_dir: Override base directory (for testing)
        """
        self.analyses_dir = base_dir or ANALYSES_DIR
        self.analyses_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Storage directory: {self.analyses_dir}")

    def save_analysis(self, analysis_data: Dict[str, Any]) -> Path:
        """Save analysis to timestamped JSON file.

        Args:
            analysis_data: Dictionary containing analysis results

        Returns:
            Path to saved file

        Raises:
            StorageWriteError: If save fails
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{timestamp}.json"
        filepath = self.analyses_dir / filename

        try:
            # Add metadata
            analysis_data["timestamp"] = timestamp
            analysis_data["version"] = "0.2.0"

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(analysis_data, f, indent=2, default=str)

            logger.info(f"✓ Analysis saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save analysis: {e}", exc_info=True)
            raise StorageWriteError(str(filepath), str(e))

    def load_all_analyses(self) -> List[Dict[str, Any]]:
        """Load all previous analyses sorted by timestamp (newest first).

        Returns:
            List of analysis dictionaries

        Raises:
            StorageReadError: If load fails
        """
        analyses = []
        try:
            for file in sorted(self.analyses_dir.glob("*.json"), reverse=True):
                try:
                    with open(file, encoding="utf-8") as f:
                        data = json.load(f)
                        # Validate basic structure
                        if "projects" in data and "overall" in data:
                            analyses.append(data)
                        else:
                            logger.warning(f"Invalid analysis file: {file}")
                except json.JSONDecodeError as e:
                    logger.warning(f"Could not parse {file}: {e}")
                except Exception as e:
                    logger.warning(f"Could not load {file}: {e}")
        except Exception as e:
            logger.error(f"Error loading analyses: {e}", exc_info=True)
            raise StorageReadError(str(self.analyses_dir), str(e))

        logger.debug(f"Loaded {len(analyses)} analyses")
        return analyses

    def load_latest_analysis(self) -> Optional[Dict[str, Any]]:
        """Load the most recent analysis.

        Returns:
            Most recent analysis or None if none exist
        """
        try:
            analyses = self.load_all_analyses()
            return analyses[0] if analyses else None
        except Exception as e:
            logger.error(f"Failed to load latest analysis: {e}")
            return None

    def get_analysis_count(self) -> int:
        """Get total number of stored analyses.

        Returns:
            Count of analysis files
        """
        try:
            return len(list(self.analyses_dir.glob("*.json")))
        except Exception as e:
            logger.error(f"Failed to count analyses: {e}")
            return 0

    def clear_analyses(self) -> None:
        """Clear all stored analyses (use with caution).

        Raises:
            StorageWriteError: If clear fails
        """
        count = 0
        try:
            for file in self.analyses_dir.glob("*.json"):
                file.unlink()
                count += 1
            logger.info(f"Cleared {count} analyses")
        except Exception as e:
            logger.error(f"Error clearing analyses: {e}", exc_info=True)
            raise StorageWriteError(str(self.analyses_dir), str(e))

    def delete_analysis(self, filename: str) -> None:
        """Delete a specific analysis file.

        Args:
            filename: Name of file to delete (e.g., "2025-11-05_10-30-45.json")

        Raises:
            StorageWriteError: If delete fails
            ValueError: If filename contains path traversal attempts
        """
        try:
            # ✅ SECURITY FIX: Prevent path traversal attacks (CWE-22)
            # Block attempts to escape the analyses directory
            if "/" in filename or "\\" in filename or filename.startswith("."):
                error_msg = f"Invalid filename - path traversal attempt detected: {filename}"
                logger.error(f"Security: {error_msg}")
                raise ValueError(error_msg)

            filepath = self.analyses_dir / filename

            # ✅ SECURITY FIX: Verify resolved path is within base directory
            # This prevents symlink attacks and other path manipulation
            try:
                resolved_path = filepath.resolve()
                base_dir = self.analyses_dir.resolve()

                # Ensure the resolved path is within the base directory
                if not str(resolved_path).startswith(str(base_dir)):
                    error_msg = f"Path traversal security violation: {filename}"
                    logger.error(f"Security: {error_msg}")
                    raise ValueError(error_msg)
            except ValueError:
                # Re-raise ValueError from path validation
                raise

            if filepath.exists():
                filepath.unlink()
                logger.info(f"Deleted analysis: {filename}")
            else:
                logger.warning(f"Analysis not found: {filename}")
        except ValueError as e:
            # Path traversal or validation error
            logger.error(f"Security error deleting analysis: {e}")
            raise StorageWriteError(str(filename), str(e))
        except Exception as e:
            logger.error(f"Error deleting analysis: {e}", exc_info=True)
            raise StorageWriteError(str(filename), str(e))
