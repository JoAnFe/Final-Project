import asyncio
from bleak import BleakClient, BleakScanner

WIFI_SSID = "FarmNet"
WIFI_PASS = "SuperSecret123"
BROKER = "192.168.1.10"
SERVICE_UUID = "0000feed-0000-1000-8000-00805f9b34fb"
CHAR_SSID =   "0000fee1-0000-1000-8000-00805f9b34fb"
CHAR_PASS =   "0000fee2-0000-1000-8000-00805f9b34fb"
CHAR_BROKER = "0000fee3-0000-1000-8000-00805f9b34fb"

async def provision():
    dev = await BleakScanner.find_device_by_filter(lambda d, ad: "ESP32-PROV" in d.name)
    async with BleakClient(dev) as cli:
        await cli.write_gatt_char(CHAR_SSID, WIFI_SSID.encode(), response=True)
        await cli.write_gatt_char(CHAR_PASS, WIFI_PASS.encode(), response=True)
        await cli.write_gatt_char(CHAR_BROKER, BROKER.encode(), response=True)
        print("Provisioned.")

if __name__ == "__main__":
    asyncio.run(provision())