# Example: A simple Unix  echo server

from curio import run, unix_server


client_count = 0
async def echo_handler(client, _):
    global client_count
    client_count += 1
    this_client = str(client_count)
    print('New Connection [' + this_client + ']')
    while True:
        data = await client.recv(10000)
        if not data:
            break
        await client.sendall(data)
    print('Connection ['+ this_client + '] closed')

if __name__ == '__main__':
    import os
    try:
        os.remove('/tmp/curiounixecho')
    except:
        pass
    try:
        print('starting unix domain server at /tmp/curiounixecho')
        run(unix_server, '/tmp/curiounixecho', echo_handler)
    except KeyboardInterrupt:
        pass
