from supabase import create_client, Client
from app.config import settings
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase clients
supabase: Client = create_client(settings.supabase_url, settings.supabase_key)
supabase_admin: Client = create_client(settings.supabase_url, settings.supabase_service_key)


async def init_db():
    """Initialize database tables if they don't exist"""
    try:
        # Check if Supabase is properly configured
        if (settings.supabase_url == "https://placeholder.supabase.co" or 
            settings.supabase_key == "placeholder_key"):
            logger.warning("⚠️  Supabase not configured - using placeholder credentials")
            logger.info("To connect to a real database, update your .env file with:")
            logger.info("  SUPABASE_URL=your_supabase_url")
            logger.info("  SUPABASE_KEY=your_supabase_anon_key") 
            logger.info("  SUPABASE_SERVICE_KEY=your_supabase_service_key")
            return
            
        # Test connection with a simple query
        result = supabase.table('users').select('id').limit(1).execute()
        logger.info("✅ Database connection successful")
        
        # Check if required tables exist by trying to query them
        tables_to_check = [
            'users', 'projects', 'files', 'tags', 'annotations', 
            'project_members', 'usage_stats'
        ]
        
        for table in tables_to_check:
            try:
                supabase.table(table).select('*').limit(1).execute()
                logger.info(f"✅ Table '{table}' exists")
            except Exception as e:
                logger.warning(f"⚠️  Table '{table}' may not exist: {e}")
        
        logger.info("Database initialization complete")
        
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        logger.error("Please ensure Supabase is configured and tables are created")
        raise


def get_db() -> Client:
    """Dependency to get database client"""
    return supabase


def get_admin_db() -> Client:
    """Get admin database client for privileged operations"""
    return supabase_admin


# Helper functions for common database operations
class DatabaseHelper:
    """Helper class for common database operations"""
    
    @staticmethod
    def paginate_query(query, page: int = 1, per_page: int = 10):
        """Add pagination to a query"""
        offset = (page - 1) * per_page
        return query.range(offset, offset + per_page - 1)
    
    @staticmethod
    def filter_by_user(query, user_id: str, user_field: str = 'user_id'):
        """Filter query by user ID"""
        return query.eq(user_field, user_id)
    
    @staticmethod
    def filter_by_project(query, project_id: str, project_field: str = 'project_id'):
        """Filter query by project ID"""
        return query.eq(project_field, project_id)
    
    @staticmethod
    def order_by_created(query, ascending: bool = False):
        """Order query by created_at timestamp"""
        return query.order('created_at', desc=not ascending)
    
    @staticmethod
    def order_by_updated(query, ascending: bool = False):
        """Order query by updated_at timestamp"""
        return query.order('updated_at', desc=not ascending)
    
    @staticmethod
    def filter_active(query, is_active_field: str = 'is_active'):
        """Filter for active records only"""
        return query.eq(is_active_field, True)
    
    @staticmethod
    def handle_db_error(error: Exception) -> Dict[str, Any]:
        """Handle database errors and return formatted response"""
        logger.error(f"Database error: {error}")
        return {
            "success": False,
            "error": str(error),
            "code": "DATABASE_ERROR"
        }
    
    @staticmethod
    def format_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
        """Format successful database response"""
        return {
            "success": True,
            "data": data,
            "message": message
        }


# Database operations wrapper
class DatabaseOperations:
    """Wrapper class for database operations with error handling"""
    
    def __init__(self, client: Client):
        self.client = client
        self.helper = DatabaseHelper()
    
    async def create_record(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in the specified table"""
        try:
            result = self.client.table(table).insert(data).execute()
            return self.helper.format_success_response(
                result.data[0] if result.data else None,
                "Record created successfully"
            )
        except Exception as e:
            return self.helper.handle_db_error(e)
    
    async def get_record(self, table: str, record_id: str, id_field: str = 'id') -> Dict[str, Any]:
        """Get a single record by ID"""
        try:
            result = self.client.table(table).select('*').eq(id_field, record_id).execute()
            data = result.data[0] if result.data else None
            return self.helper.format_success_response(data)
        except Exception as e:
            return self.helper.handle_db_error(e)
    
    async def update_record(self, table: str, record_id: str, data: Dict[str, Any], id_field: str = 'id') -> Dict[str, Any]:
        """Update a record by ID"""
        try:
            result = self.client.table(table).update(data).eq(id_field, record_id).execute()
            return self.helper.format_success_response(
                result.data[0] if result.data else None,
                "Record updated successfully"
            )
        except Exception as e:
            return self.helper.handle_db_error(e)
    
    async def delete_record(self, table: str, record_id: str, id_field: str = 'id') -> Dict[str, Any]:
        """Delete a record by ID"""
        try:
            result = self.client.table(table).delete().eq(id_field, record_id).execute()
            return self.helper.format_success_response(
                None,
                "Record deleted successfully"
            )
        except Exception as e:
            return self.helper.handle_db_error(e)
    
    async def list_records(self, table: str, filters: Optional[Dict[str, Any]] = None, 
                          page: int = 1, per_page: int = 10, order_by: str = 'created_at') -> Dict[str, Any]:
        """List records with pagination and filtering"""
        try:
            query = self.client.table(table).select('*')
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    query = query.eq(field, value)
            
            # Apply pagination
            query = self.helper.paginate_query(query, page, per_page)
            
            # Apply ordering
            query = query.order(order_by, desc=True)
            
            result = query.execute()
            
            # Get total count for pagination
            count_query = self.client.table(table).select('id', count='exact')
            if filters:
                for field, value in filters.items():
                    count_query = count_query.eq(field, value)
            
            count_result = count_query.execute()
            total = count_result.count if count_result.count else 0
            
            return self.helper.format_success_response({
                'items': result.data,
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            })
        except Exception as e:
            return self.helper.handle_db_error(e)


# Create global database operations instance
db_ops = DatabaseOperations(supabase)
