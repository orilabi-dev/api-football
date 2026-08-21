from airflow.providers.http.hooks.http import HttpHook

from dag_utils.config import HTTP_CONNECTION_ID


class ApiFootballClient:
    def __init__(self, connection_id=HTTP_CONNECTION_ID):
        self.hook = HttpHook(method="GET", http_conn_id=connection_id)

    def get_leagues(self):
        conn = self.hook.get_connection(self.hook.http_conn_id)

        print(conn.host)
        print(f"Password: {conn.password}")

        response = self.hook.run(
            endpoint="/leagues", headers={"x-apisports-key": conn.password}
        )

        response.raise_for_status()

        return response.json()
