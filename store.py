import os
from influxdb_client_3 import InfluxDBClient3, Point
from six.moves import _thread

class Store:
    def __init__(self):
        url = os.getenv('INFLUXDB_URL')
        token = os.getenv('INFLUXDB_TOKEN')
        org = os.getenv('INFLUXDB_ORG')
        bucket = os.getenv('INFLUXDB_BUCKET')

        self.client = InfluxDBClient3(host=url, token=token, org=org)
        self.bucket = bucket

    def write_point(self, measurement, tags, fields):
        point = Point(measurement)
        
        for tag_key, tag_value in tags.items():
            point = point.tag(tag_key, tag_value)
        
        for field_key, field_value in fields.items():
            point = point.field(field_key, field_value)
        
        self.client.write(database=self.bucket, record=point)

    def close(self):
        self.client.close()

# Usage example:
# store = Store()
# store.write_point("room_data", {"room": "W48N55"}, {"energy": 1000, "structures": 50})
# store.close()
