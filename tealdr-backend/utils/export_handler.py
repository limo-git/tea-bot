import json
import csv
from datetime import datetime
from io import StringIO, BytesIO
from utils.logger import get_logger

logger = get_logger(__name__)

class ExportHandler:
    """Handle exporting search results to various formats."""
    
    @staticmethod
    async def export_to_json(messages, query, user):
        """Export messages to JSON format."""
        try:
            export_data = {
                'query': query,
                'exported_by': str(user),
                'exported_at': datetime.utcnow().isoformat(),
                'total_messages': len(messages),
                'messages': []
            }
            
            for msg in messages:
                export_data['messages'].append({
                    'author': msg.get('author_name'),
                    'content': msg.get('content'),
                    'timestamp': msg.get('created_at'),
                    'channel_id': msg.get('channel_id'),
                    'message_id': msg.get('message_id')
                })
            
            json_str = json.dumps(export_data, indent=2)
            file_buffer = BytesIO(json_str.encode('utf-8'))
            
            filename = f"search_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            return file_buffer, filename
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return None, None
    
    @staticmethod
    async def export_to_csv(messages, query, user):
        """Export messages to CSV format."""
        try:
            output = StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Author', 'Content', 'Timestamp', 'Channel ID', 'Message ID'])
            
            # Write data
            for msg in messages:
                writer.writerow([
                    msg.get('author_name', ''),
                    msg.get('content', ''),
                    msg.get('created_at', ''),
                    msg.get('channel_id', ''),
                    msg.get('message_id', '')
                ])
            
            csv_str = output.getvalue()
            file_buffer = BytesIO(csv_str.encode('utf-8'))
            
            filename = f"search_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            return file_buffer, filename
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return None, None
    
    @staticmethod
    async def export_to_markdown(messages, query, user):
        """Export messages to Markdown format."""
        try:
            md_lines = [
                f"# Search Results",
                f"",
                f"**Query:** {query}",
                f"**Exported by:** {user}",
                f"**Date:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
                f"**Total Messages:** {len(messages)}",
                f"",
                f"---",
                f""
            ]
            
            for i, msg in enumerate(messages, 1):
                author = msg.get('author_name', 'Unknown')
                content = msg.get('content', '')
                timestamp = msg.get('created_at', '')
                
                md_lines.extend([
                    f"## {i}. {author}",
                    f"*{timestamp}*",
                    f"",
                    content,
                    f"",
                    f"---",
                    f""
                ])
            
            md_str = "\n".join(md_lines)
            file_buffer = BytesIO(md_str.encode('utf-8'))
            
            filename = f"search_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
            return file_buffer, filename
            
        except Exception as e:
            logger.error(f"Error exporting to Markdown: {e}")
            return None, None
    
    @staticmethod
    async def export_to_txt(messages, query, user):
        """Export messages to plain text format."""
        try:
            txt_lines = [
                f"Search Results",
                f"=" * 50,
                f"",
                f"Query: {query}",
                f"Exported by: {user}",
                f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
                f"Total Messages: {len(messages)}",
                f"",
                f"=" * 50,
                f""
            ]
            
            for i, msg in enumerate(messages, 1):
                author = msg.get('author_name', 'Unknown')
                content = msg.get('content', '')
                timestamp = msg.get('created_at', '')
                
                txt_lines.extend([
                    f"",
                    f"[{i}] {author} - {timestamp}",
                    f"-" * 50,
                    content,
                    f""
                ])
            
            txt_str = "\n".join(txt_lines)
            file_buffer = BytesIO(txt_str.encode('utf-8'))
            
            filename = f"search_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
            return file_buffer, filename
            
        except Exception as e:
            logger.error(f"Error exporting to TXT: {e}")
            return None, None

export_handler = ExportHandler()
