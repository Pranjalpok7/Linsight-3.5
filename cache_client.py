# cache_client.py
import redis
import json

class CacheClient:
    def __init__(self, host='redis', port=6379, db=0, ttl=3600):
        # 'redis' is the service name from docker-compose.yml
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.ttl = ttl # Time-to-live in seconds (e.g., 1 hour)

    def get(self, key: str):
        """Gets a value from the cache. Returns None if not found."""
        value = self.client.get(key)
        return json.loads(value) if value else None

    def set(self, key: str, value: dict):
        """Sets a value in the cache with a TTL."""
        # We serialize the dictionary to a JSON string for storage
        self.client.setex(key, self.ttl, json.dumps(value))