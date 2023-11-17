import enum
import io
import logging
import os
from typing import List

import paramiko
from mysql.connector import connect
from pydantic.dataclasses import dataclass
from sshtunnel import SSHTunnelForwarder

from minimal_ai.app.connections.sql_base import Connection

logger = logging.getLogger(__name__)


class ConnMethod(str, enum.Enum):
    DIRECT = "direct"
    SSH_TUNNEL = "ssh_tnnel"


@dataclass
class MySql(Connection):
    database: str
    host: str
    password: str
    username: str
    port: int = 3306
    connection_method: ConnMethod = ConnMethod.DIRECT
    ssh_host: str | None = None
    ssh_port: int = 22
    ssh_username: str | None = None
    ssh_password: str | None = None
    ssh_key_path: str | None = None
    ssh_tunnel = None

    def build_connection(self):
        """method to build db connection"""
        host = self.host
        port = self.port
        if self.connection_method == ConnMethod.SSH_TUNNEL:
            ssh_setting = dict(ssh_username=self.ssh_username)
            if self.ssh_key_path is not None:
                if os.path.exists(self.ssh_key_path):
                    ssh_setting["ssh_key"] = self.ssh_key_path
                else:
                    ssh_setting["ssh_key"] = paramiko.RSAKey.from_private_key(  # type: ignore
                        io.StringIO(self.ssh_key_path),
                    )
            else:
                ssh_setting["ssh_password"] = self.ssh_password

            self.ssh_tunnel = SSHTunnelForwarder(
                (self.ssh_host, self.ssh_port),
                remote_bind_address=(self.host, self.port),
                local_bind_address=("", self.port),
                **ssh_setting,  # type: ignore
            )
            self.ssh_tunnel.start()
            self.ssh_tunnel._check_is_started()

            host = "127.0.0.1"
            port = self.ssh_tunnel.local_bind_port

        return connect(
            database=self.database,
            host=host,
            password=self.password,
            port=port,
            user=self.username,
        )

    def close_connection(self, connection):
        """method to close db connection"""
        connection.close()
        if self.ssh_tunnel is not None:
            self.ssh_tunnel.stop()
            self.ssh_tunnel = None

    def get_information_schema(self, table_name: str | None = None) -> List[dict]:
        """method to get the information schema"""
        query = f"""
        SELECT
            TABLE_NAME
            , COLUMN_DEFAULT
            , COLUMN_KEY
            , COLUMN_NAME
            , cast(COLUMN_TYPE as char(20)) as COLUMN_TYPE
            , IS_NULLABLE
        FROM information_schema.columns
        WHERE table_schema = '{self.database}'
        """
        if table_name:
            query = f"{query} AND TABLE_NAME in ('{table_name}')"

        return self.execute(query)
