import asyncio
from bleak import BleakClient

# Your device's specifics
address = "23:01:02:1D:58:1C"  # The Bluetooth address of your light
uuid = "0000afd1-0000-1000-8000-00805f9b34fb"  # UUID for the characteristic controlling the light
ON_HEX = "5bf000b5"  # Hex command to turn the light on
RED_HEX = "0000ff"  # Assuming RED_HEX is the correct format for setting color

async def set_light_color(client: BleakClient, color_hex: str) -> None:
    """
    Sends a color command to the RGB light.
    """
    # Assuming the color command structure; adjust as needed for your device
    header = bytes.fromhex("5a 00 01")
    footer = bytes.fromhex("00 a5")
    color_bytes = bytes.fromhex(color_hex.replace(" ", ""))  # Remove spaces and convert to bytes
    value = header + color_bytes + footer
    await client.write_gatt_char(uuid, value)
    print(f"Set the light color to #{color_hex}.")

async def toggle_on(client: BleakClient) -> None:
    """
    Turns the RGB light on.
    """
    await client.write_gatt_char(uuid, bytes.fromhex(ON_HEX))
    print("Turned on")

async def main(address: str) -> None:
    """
    Main function to control the RGB light.
    """
    async with BleakClient(address, timeout=30) as client:
        await toggle_on(client)
        await asyncio.sleep(1)  # Wait a bit after turning on
        await set_light_color(client, RED_HEX)  # Set to red

if __name__ == "__main__":
    asyncio.run(main(address))
