import binascii
import socket
import asyncio
import configparser
import threading
import os
import argparse
import pyodbc  # Importing pyodbc for SQL Server connection
from concurrent.futures import ThreadPoolExecutor
from logger import Logger
from redis_uploader import RedisUploader


class Server:
    def __init__(self, config_file=None):
        self.config = configparser.ConfigParser()
        self.load_configuration(config_file)
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_host, self.server_port))
        self.server_socket.listen(self.max_clients)
        self.redis_uploader = RedisUploader(self.redis_host, self.redis_port, self.log_dir)

        print(f"Server listening on {self.server_host}:{self.server_port}")
        self.clients = {}
        self.lock = threading.Lock()
        self.logger = Logger(self.log_dir)  # Initialize the logger
        self.executor = ThreadPoolExecutor(max_workers=self.max_clients)
        self.db_connection = self.connect_to_database()

    def load_configuration(self, config_file):
        if config_file and os.path.exists(config_file):
            self.config.read(config_file)
            self.server_host = self.config.get('Server', 'host')
            self.server_port = self.config.getint('Server', 'port')
            self.max_clients = self.config.getint('Server', 'max_clients')
            self.redis_host = self.config.get('Redis', 'host')
            self.redis_port = self.config.getint('Redis', 'port')
            self.redis_key = self.config.get('Redis', 'redis_key')
            self.log_dir = self.config.get('Logging', 'log_dir')
            self.db_driver = self.config.get('Database', 'driver')
            self.db_server = self.config.get('Database', 'server')
            self.db_database = self.config.get('Database', 'database')
            self.db_username = self.config.get('Database', 'username')
            self.db_password = self.config.get('Database', 'password')
         
        else:
            print(f"Config file not provided or does not exist. Using environment variables or default values.")

    def connect_to_database(self):
        connection_string = f"DRIVER={self.db_driver};SERVER={self.db_server};DATABASE={self.db_database};UID={self.db_username};PWD={self.db_password}"
        return pyodbc.connect(connection_string)

    def handle_client(self, client_socket, client_address):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._handle_client(client_socket, client_address))
        loop.close()

    async def _handle_client(self, client_socket, client_address):
        try:
            print(f"Device connected: {client_address}")
            imei_data = await asyncio.to_thread(client_socket.recv, 2048)
            imei_len = int.from_bytes(imei_data[:2], byteorder='big')
            imei = imei_data[2:2 + imei_len].decode('utf-8')

            if self.is_valid_imei(imei):
                await asyncio.to_thread(client_socket.sendall, b'\x01')  # Send acknowledgment 0x01
                with self.lock:
                    self.clients[imei] = (client_socket, client_address)
            else:
                await asyncio.to_thread(client_socket.sendall, b'\x00')  # Send rejection 0x00
                client_socket.close()
                return

            while True:
                data = await asyncio.to_thread(client_socket.recv, 2048)
                if not data:
                    break
                hex_data = data.hex()
                if hex_data[16:22] == "0c0106":
                    self.logger.log("Response", f"{hex_data}", log_level="INFO")
                else:
                    message = f'{imei}|{hex_data}'
                    self.redis_uploader.upload_record(self.redis_key, message)
                    num_of_data = int(hex_data[18:20], 16)
                    acknowledgment = num_of_data.to_bytes(4, byteorder='big')
                    await asyncio.to_thread(client_socket.sendall, acknowledgment)                
                    self.logger.log("RawData", f"RawData: {hex_data}", log_level="INFO")

                command = self.get_command_from_database(imei)
                if command:
                    await self.send_command_to_device(imei, command)
                    
        except Exception as e:
            self.logger.log("HandleClientError", f"Error handling client: {e}", log_level="ERROR")
        finally:
            with self.lock:
                if imei in self.clients:
                    del self.clients[imei]
            client_socket.close()

    def is_valid_imei(self, imei):
        return True

    def get_command_from_database(self, imei):
        cursor = self.db_connection.cursor()
        try:
            cursor.execute("SELECT TOP 1 cmdstr FROM teltonikaout WHERE MCTID = ? AND recstatus = 0", imei)
            result = cursor.fetchone()
            if result:
                command = result[0]
                cursor.execute("UPDATE teltonikaout SET recstatus = 1 WHERE MCTID = ? AND cmdstr = ?", imei, command)
                self.db_connection.commit()
                return command
        except Exception as e:
            self.logger.log("DatabaseError", f"Error fetching command from database: {e}", log_level="ERROR")
        return None

    async def send_command_to_device(self, imei, command):
        with self.lock:
            if imei in self.clients:
                client_socket, client_address = self.clients[imei]
                try:
                    print(f"Sending command to IMEI {imei}: {command}")
                    self.logger.log("SendCommand", f"Sending command to IMEI {imei}: {command}", log_level="INFO")
                    command_bytes = binascii.unhexlify(command)
                    await self._send_command(client_socket, command_bytes)
                    print(f"Command sent to IMEI {imei}")
                    self.logger.log("SendCommand", f"Command sent to IMEI {imei}", log_level="INFO")
                except Exception as e:
                    self.logger.log("SendCommandError", f"Error sending command to {imei}: {e}", log_level="ERROR")

    async def _send_command(self, client_socket, command_bytes):
        await asyncio.to_thread(client_socket.sendall, command_bytes)

    async def client_acceptance(self):
        loop = asyncio.get_event_loop()
        while True:
            client_socket, client_address = await loop.sock_accept(self.server_socket)
            if len(self.clients) < self.max_clients:
                loop.run_in_executor(self.executor, self.handle_client, client_socket, client_address)
            else:
                client_socket.close()

    def start_server(self):
        try:
            asyncio.run(self.main_server())
        except KeyboardInterrupt:
            self.logger.log("ServerShutdown", "Server shutting down.", log_level="INFO")
            self.executor.shutdown(wait=True)
            
    async def main_server(self):
        await asyncio.gather(self.client_acceptance())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Server Configuration')
    parser.add_argument('--config', type=str, help='Path to the configuration file')
    args = parser.parse_args()
    config_file = args.config if args.config else None
    server = Server(config_file)
    server.start_server()
