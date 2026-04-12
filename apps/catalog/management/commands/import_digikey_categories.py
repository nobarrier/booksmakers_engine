from django.core.management.base import BaseCommand

from apps.catalog.services.importers.digikey_importer import run_import

DIGIKEY_CATEGORY_KEYWORDS = [
    # MCU / 개발보드
    "arduino",
    "raspberry pi",
    "esp32",
    "stm32",
    "nrf52",
    # 센서
    "temperature sensor",
    "humidity sensor",
    "imu sensor",
    "pressure sensor",
    "lidar sensor",
    # 전원
    "dc dc converter",
    "power module",
    "battery charger",
    "bms board",
    # 통신
    "wifi module",
    "bluetooth module",
    "lora module",
    "zigbee module",
    # 로봇
    "servo motor",
    "stepper motor",
    "motor driver",
    "robot controller",
]


class Command(BaseCommand):
    help = "Import Digikey categories"

    def handle(self, *args, **options):
        for keyword in DIGIKEY_CATEGORY_KEYWORDS:
            print("\n==============================")
            print("IMPORT CATEGORY:", keyword)
            print("==============================\n")

            run_import(keyword)

        print("\nAll category imports completed.\n")
