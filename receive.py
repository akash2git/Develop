import websockets
import asyncio
import pyodbc

# Connection parameters
server = 'KLBLRLP1620'
database = 'Food_Order'
username = 'sa'
password = 'root@123'
driver = '{ODBC Driver 17 for SQL Server}' # This driver works for most modern SQL Server installations

async def receive_message(websocket):
    message = await websocket.recv()
    print(f"Received: {message}")

try:
    # Create a connection string
    conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    # Connect to the database
    conn = pyodbc.connect(conn_str)

    # Create a cursor
    cursor = conn.cursor()

    query = "select * from kimchi_userprofile"
    cursor.execute(query)

    # Fetch the data
    rows = cursor.fetchall()

    # Process the data
    if rows:
        for row in rows:
            print(row)
            host = row[2]
            # Start the server
            start_server = websockets.serve(receive_message, host, 8765)
            asyncio.get_event_loop().run_until_complete(start_server)
            asyncio.get_event_loop().run_forever()
            continue
except Exception as e:
    print(e)
