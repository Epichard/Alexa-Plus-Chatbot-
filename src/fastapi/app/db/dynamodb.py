"""
DynamoDB client and connection management
"""

import aioboto3
import logging
from typing import Optional
from ..core.config import settings

logger = logging.getLogger(__name__)

# Global DynamoDB resource
_dynamodb_resource = None


async def init_dynamodb():
    """Initialize DynamoDB connection"""
    global _dynamodb_resource
    
    try:
        session = aioboto3.Session()
        
        # Configure DynamoDB connection
        dynamodb_config = {
            'region_name': settings.AWS_REGION
        }
        
        # Add endpoint URL for local development
        if settings.DYNAMODB_ENDPOINT_URL:
            dynamodb_config['endpoint_url'] = settings.DYNAMODB_ENDPOINT_URL
            
        # Add credentials if provided
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            dynamodb_config.update({
                'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
                'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY
            })
        
        _dynamodb_resource = session.resource('dynamodb', **dynamodb_config)
        logger.info("DynamoDB connection initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize DynamoDB connection: {str(e)}")
        raise


def get_dynamodb_client():
    """Get DynamoDB resource"""
    if _dynamodb_resource is None:
        raise RuntimeError("DynamoDB not initialized. Call init_dynamodb() first.")
    return _dynamodb_resource


async def get_table(table_name: str):
    """Get DynamoDB table"""
    dynamodb = get_dynamodb_client()
    return await dynamodb.Table(table_name)


async def create_tables_if_not_exist():
    """Create DynamoDB tables if they don't exist"""
    dynamodb = get_dynamodb_client()
    
    # Table definitions
    tables = [
        {
            'TableName': settings.DYNAMODB_TABLE_CALLS,
            'KeySchema': [
                {'AttributeName': 'event_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'event_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'},
                {'AttributeName': 'resident_id', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'timestamp-index',
                    'KeySchema': [
                        {'AttributeName': 'timestamp', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'BillingMode': 'PAY_PER_REQUEST'
                },
                {
                    'IndexName': 'resident-index',
                    'KeySchema': [
                        {'AttributeName': 'resident_id', 'KeyType': 'HASH'},
                        {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'BillingMode': 'PAY_PER_REQUEST'
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': settings.DYNAMODB_TABLE_RESIDENTS,
            'KeySchema': [
                {'AttributeName': 'resident_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'resident_id', 'AttributeType': 'S'},
                {'AttributeName': 'room_number', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'room-index',
                    'KeySchema': [
                        {'AttributeName': 'room_number', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'BillingMode': 'PAY_PER_REQUEST'
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': settings.DYNAMODB_TABLE_USERS,
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'username', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'username-index',
                    'KeySchema': [
                        {'AttributeName': 'username', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'BillingMode': 'PAY_PER_REQUEST'
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        }
    ]
    
    try:
        for table_def in tables:
            table_name = table_def['TableName']
            try:
                # Check if table exists
                table = await dynamodb.Table(table_name)
                await table.load()
                logger.info(f"Table {table_name} already exists")
            except Exception:
                # Table doesn't exist, create it
                logger.info(f"Creating table {table_name}")
                await dynamodb.create_table(**table_def)
                logger.info(f"Table {table_name} created successfully")
                
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        # Don't raise in production - tables might be managed externally