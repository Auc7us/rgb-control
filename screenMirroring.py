import asyncio
from bleak import BleakClient
from colorthief import ColorThief
import io
from PIL import ImageGrab

address = "23:01:02:1D:58:1C"  # The Bluetooth address of your light
uuid = "0000afd1-0000-1000-8000-00805f9b34fb"  # UUID for the characteristic controlling the light
Is_On = 1
should_continue = True
ON_HEX = "5bf000b5"
OFF_HEX = "5b0f00b5"

client = BleakClient

async def send_command(Client: BleakClient, color = "ff ff ff", dim = "64", speed = "00"):
    header = bytes.fromhex("5a 00 01")
    footer = bytes.fromhex("00 a5")
    value = header + bytes.fromhex(color) + bytes.fromhex(speed) + bytes.fromhex(dim) + footer
    await Client.write_gatt_char(uuid, value)

# inbuild effects hex: str 80-96; int 0-22
async def effects(Client: BleakClient, mod = "80", dim = "64", speed = "00"):
    if isinstance(mod, int):
        value = int(128 + mod).to_bytes(1,"big")
    else:
        value = bytes.fromhex(mod)
    header = bytes.fromhex("5c 00")
    footer = bytes.fromhex("00 c5")
    await Client.write_gatt_char(uuid, header + value + bytes.fromhex(speed) + bytes.fromhex(dim) + footer)

# inbuild effects: mod 01-04; speed 01-08
async def mic_effect(Client: BleakClient, mod = "01", level = "01"):
    if isinstance(mod, int):
        value = int(mod).to_bytes(1,"big")
    else:
        value = bytes.fromhex(mod)
    if isinstance(level, int):
        value1 = int(level).to_bytes(1,"big")
    else:
        value1 = bytes.fromhex(level)
    header = bytes.fromhex("5a 01 f0")
    footer = bytes.fromhex("a5")
    await Client.write_gatt_char(uuid, header + value + value1 + footer)

async def toggle_on(Client: BleakClient, _uuid = uuid) -> None:
    await Client.write_gatt_char(_uuid, bytes.fromhex(ON_HEX))
    print("Turned on")

async def toggle_off(Client: BleakClient, _uuid = uuid) -> None:
    await Client.write_gatt_char(_uuid, bytes.fromhex(OFF_HEX))
    print("Turned off")

async def init_client(address: str) -> BleakClient:
    client =  BleakClient(address)  
    print("Connecting")
    await client.connect()
    print(f"Connected to {address}")
    return client
    
async def disconnect_client(client: BleakClient) -> None:
    await client.disconnect()
    print("Disconnected")
    
async def on_exit(Client = client) -> None:
    if Client is not None:
        await disconnect_client(client)
    print("Exited")
    
# setup screenshot region
screen_width, screen_height = ImageGrab.grab().size
region_width = 640
region_height = 480
region_left = (screen_width - region_width) // 2
region_top = (screen_height - region_height) // 2
screen_region = (region_left, region_top, region_left + region_width, region_top + region_height)

screenshot_memory = io.BytesIO(b"")

def get_dominant_colour() -> str:
    try:
        screenshot = ImageGrab.grab(screen_region)
        screenshot_memory.seek(0)
        screenshot_memory.truncate(0)
        screenshot.save("tmp.png") 
        color_thief = ColorThief("tmp.png")
        # Get the dominant color
        dominant_color = color_thief.get_color(quality=20)
        return '{:02x}{:02x}{:02x}'.format(*dominant_color)
    except Exception as e:
        print(f"Error: {e}")
        return "ff ff ff"


async def loop_dominant_color(Client: BleakClient, gap=0.10, dim="64", speed="00"):
    global should_continue
    while should_continue:
        await send_command(Client, get_dominant_colour(), dim, speed)
        await asyncio.sleep(gap)  # Use asyncio.sleep instead of time.sleep for async compatibility

async def main(address):
    client = BleakClient(address)
    try:
        print("Connecting")
        await client.connect()
        print("Connected")
        await toggle_on(client, uuid)
        # Initialize and run your main work here, for example:
        # await send_command(client, "ff ff ff", "64", "00")
        # Instead of a continuous loop, let's say you're doing a single task
        await loop_dominant_color(client, 0.12, "10", "00")
    except Exception as e:
        print(f"An error occurred during main operation: {e}")
    finally:
        print("Cleaning up...")
        await client.disconnect()
        print("Disconnected")

async def run_main(address):
    loop = asyncio.get_event_loop()
    task = loop.create_task(main(address))
    try:
        await task
    except asyncio.CancelledError:
        print("Task was cancelled, cleanup should have been done")

if __name__ == "__main__":
    try:
        asyncio.run(run_main(address))
    except KeyboardInterrupt:
        print("Detected KeyboardInterrupt, stopping...")
        # Here we assume that run_main and its tasks handle cleanup properly
