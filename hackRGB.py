from bluepy import btle

class MyLight(btle.Peripheral):
    def __init__(self, addr):
        super().__init__(addr)

device_address = '23:01:02:1D:58:1C'

try:
    print(f"Connecting to {device_address}...")
    light = MyLight(device_address)
    print("Connected. Discovering services...")
    
    # Get the specific service you're interested in
    specific_service = light.getServiceByUUID('afd0')
    print(f"Discovered service {specific_service}")
    
    # Discover and print all characteristics for this service
    characteristics = specific_service.getCharacteristics()
    for char in characteristics:
        print(f"Characteristic {char.uuid}, Handle {char.getHandle()}")
        print(f"  Properties: {char.propertiesToString()}")
        # Depending on the characteristic properties, you might also read some values
        # if 'READ' in char.propertiesToString():
        #     print(f"  Value: {char.read()}")

except Exception as e:
    print(f"Failed to connect or retrieve services: {e}")
    
    
command = bytearray([0x00, 0xFF, 0x00])  # Example command, adjust as needed

try:
    characteristic = light.getCharacteristics(uuid='0000afd1-0000-1000-8000-00805f9b34fb')[0]
    characteristic.write(command, withResponse=True)  # Use withResponse=False if you don't need confirmation
    print("Command sent.")
except Exception as e:
    print(f"Error sending command: {e}")
    
finally:
    if 'light' in locals():  # Check if 'light' is defined to avoid NameError
        light.disconnect()
        print("Disconnected.")
