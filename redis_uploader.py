import redis
import configparser
from logger import Logger

class RedisUploader:
    def __init__(self, redis_host, redis_port, log_dir):
        self.logger = Logger(log_dir)
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=0, decode_responses=True)

    def upload_record(self, redis_key, record):
        try:
            self.redis_client.rpush(redis_key, record)
        except Exception as e:
            self.logger.log("redis_error", f"Error uploading record to Redis: {e}", log_level="ERROR")

if __name__ == "__main__":
    # For testing purposes
    imei = "350612077040507"
    test_records = "00000000000003C78E0100000190395E26B0003F9D96F0066F6246000B0081070000000000F000A500EF0100F00100500100150500C80000450100010100B30000020000030100B40000ED02007108010701017F01005100005200005900006F00007200009800028C00028D00028E00028F00029000029100029200029300029400029500029600038200038300038400038500038600038700038800038900038A00038B00038C00038D00038E00038F00039000039100039200039300039400039500039600039700039800039900039A00039B00039C00039D00039E00039F0003A00003A10003A20003A30003A40003A50003A60003A70003A80003A90003AA0003AB0003AC0003AD0003AE0003AF0003B00003B10003B20003B30003B40003B50003B60003B70003B80003B90003BA0003BB0003BC0003BD0003BE0003BF0003C00003C10003C20003C30003C40003C50003C60003C70003C80003C90003CA0003CB0003CC0003CD0003CE0003CF0003D00003D10003D20003D30003D40003D50003D60003D70003D80003D90003DA0003DB0003DC0003DD0003DE0003DF0003E000043B00043C00043D00043E0004870004F60004FB00053300053400053500053600054000054100054600054700054B00054C00054D00054E00054F00055000055100055300055400055600055700055800055900055A00055B00055C00055D00055E00055F00056000056100057400057500002F00B5002900B6000F00424A830018000000CE624100430E270044000000090056000D0E7C0011FFA80012FFB60013FFFB00063F61000F03E8026E00000054000000550000005A0000006E00000073000000760000007700000078000000790000007A00000097000000A800000458000004590000048500000486000004FC000004FD000004FE000004FF00000538000005390000053A0000053B0000053D0000053E0000053F00000543000005440000054500000548000005490000001300F10000B09400C70000002000100000D56F000C0000212601C100000000027C00774108005300000000005700000000006600000000006700000000006900000000006B00000000007B000000000086000000000190000000000362000000000471000000000483000000000484000000000007000B00000002177DB180008400000000000000000205000000000000003F0206000000000000000002070000000000000000053C0000000000000000000E000000022A5FB2F60002018300222B3130373936322E393530302B313036373239322E343030302B3030302E3031312F018400110031C22F4141005600140000573153514E0100000056"
    redis_key = "Teltonika"
    message = f'{imei}|{test_records}'
    
    # Create an instance of RedisUploader
    redis_uploader = RedisUploader(redis_host='127.0.0.1', redis_port=6379, log_dir='./logs')

    redis_uploader.upload_record(redis_key, message)
