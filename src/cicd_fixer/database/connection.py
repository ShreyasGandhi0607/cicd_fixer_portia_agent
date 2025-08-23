"""Database connection management for the CI/CD Fixer Agent."""

import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor
from typing import Optional
from urllib.parse import urlparse
from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    """Manages database connections and provides connection utilities."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database connection manager.
        
        Args:
            database_url: Database connection URL. If None, uses settings.
        """
        settings = get_settings()
        self.database_url = database_url or settings.database_url
        
        if self.database_url:
            self.database_url = self._fix_database_url(self.database_url)
            logger.info("Database connection manager initialized")
        else:
            logger.warning("No DATABASE_URL provided, database features will be limited")
    
    def _fix_database_url(self, url: str) -> str:
        """Fix common issues with cloud PostgreSQL URLs for deployment compatibility.
        
        Args:
            url: Original database URL
            
        Returns:
            Fixed database URL
        """
        try:
            parsed = urlparse(url)
            
            # Reconstruct without problematic query parameters
            fixed_url = f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port or 5432}{parsed.path}"
            
            # Add SSL requirement for cloud deployment
            if 'sslmode' not in url.lower():
                fixed_url += "?sslmode=require"
            elif 'sslmode' in url.lower():
                # Keep existing SSL mode
                query_params = []
                if parsed.query:
                    for param in parsed.query.split('&'):
                        if '=' in param:
                            key, value = param.split('=', 1)
                            if key.lower() == 'sslmode':
                                query_params.append(f"sslmode={value}")
                
                if query_params:
                    fixed_url += "?" + "&".join(query_params)
                else:
                    fixed_url += "?sslmode=require"
            
            logger.info("Database URL fixed for cloud deployment compatibility")
            return fixed_url
            
        except Exception as e:
            logger.error(f"Error fixing database URL: {e}")
            logger.info(f"Using original URL: {url}")
            return url
    
    def get_connection(self):
        """Get a database connection.
        
        Returns:
            psycopg2 connection object
        """
        if not self.database_url:
            raise Exception("No database URL configured")
        
        return psycopg2.connect(self.database_url)
    
    def test_connection(self) -> bool:
        """Test the database connection.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_cursor(self, connection, cursor_factory=RealDictCursor):
        """Get a cursor with the specified factory.
        
        Args:
            connection: Database connection
            cursor_factory: Cursor factory class
            
        Returns:
            Database cursor
        """
        return connection.cursor(cursor_factory=cursor_factory)


# Global database connection instance
db_connection = DatabaseConnection()


def get_db_connection() -> DatabaseConnection:
    """Get the global database connection instance.
    
    Returns:
        Database connection manager
    """
    return db_connection
