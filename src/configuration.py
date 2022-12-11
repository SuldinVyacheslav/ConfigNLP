from typing import Final

# magic words for components
MB: Final[str] = "Motherboard"
RAM: Final[str] = "RAM"
CPU: Final[str] = "Processor"
GPU: Final[str] = "Video Card"
PB: Final[str] = "Power Block"
BODY: Final[str] = "Body"
# magic words for main info

CHIPSET: Final[str] = "chipset"
SOCKET: Final[str] = "socket"
DDR: Final[str] = "RAMstandart"
RAM_TYPE: Final[str] = "RAMtype"
ATX: Final[str] = "atx"

FREQUENCY: Final[str] = "clock"

MEM_TYPE: Final[str] = "mem"
INTAKE: Final[str] = "heat"
LENGTH: Final[str] = "len"
SLOT: Final[str] = "slot"

CPU_SOCKET: Final[str] = "socket"
HEAT_OUT: Final[str] = "heat"

CAPACITY: Final[str] = "capac"


class PCComponent:
    def __init__(self, component_type: str) -> None:
        self.main_info: dict[str, str] = {}
        self.type = component_type
        self.name = ""
        self.price = 0
        self.link = ""
        self.is_set = ""
        self.image = ""
        self.all_info = ""


class MotherBoard(PCComponent):
    def __init__(self, base: str) -> None:
        super().__init__(base)
        self.main_info = {
            CHIPSET: "",
            SOCKET: "",
            DDR: "",
            RAM_TYPE: "",
            FREQUENCY: "",
            ATX: "",
        }


class RAMemory(PCComponent):
    def __init__(self, base: str) -> None:
        super().__init__(base)
        self.main_info = {
            DDR: "",
            FREQUENCY: "",
            CAPACITY: "",
            RAM_TYPE: "",
        }


class VideoCard(PCComponent):
    def __init__(self, base: str) -> None:
        super().__init__(base)
        self.main_info = {DDR: "", INTAKE: "", SLOT: ""}


class Procesor(PCComponent):
    def __init__(self, base: str) -> None:
        super().__init__(base)
        self.main_info = {CPU_SOCKET: "", FREQUENCY: "", HEAT_OUT: ""}


class PowerBlock(PCComponent):
    def __init__(self, base: str) -> None:
        super().__init__(base)
        self.main_info = {CAPACITY: "", LENGTH: ""}


class Body(PCComponent):
    def __init__(self, base: str) -> None:
        super().__init__(base)
        self.main_info = {ATX: ""}


class Configuration:
    def __init__(self, identifier: str):
        self.id = identifier
        self.mob = MotherBoard(MB)
        self.ram = RAMemory(RAM)
        self.cpu = Procesor(CPU)
        self.gpu = VideoCard(GPU)
        self.powb = PowerBlock(PB)
        self.body = Body(BODY)

        self.problems: list[str] = []

    def get_price(self) -> int:
        return (
            self.mob.price
            + self.cpu.price
            + self.body.price
            + self.ram.price
            + self.gpu.price
            + self.powb.price
        )

    def socket_check(self) -> None:
        if (self.mob.is_set and self.cpu.is_set) and (
            not self.mob.main_info[SOCKET] == self.cpu.main_info[SOCKET]
        ):
            self.problems.append(
                "socket: "
                + self.mob.main_info[SOCKET]
                + " X "
                + self.cpu.main_info[SOCKET]
            )

    def ram_check(self) -> None:
        if self.ram.is_set and self.mob.is_set:
            if not self.mob.main_info[DDR][:4] == self.ram.main_info[DDR]:
                self.problems.append(
                    "RAM type mismatch: "
                    + self.mob.main_info[DDR][:4]
                    + " X "
                    + self.ram.main_info[DDR]
                )
            if not self.mob.main_info[RAM_TYPE] == self.ram.main_info[RAM_TYPE]:
                self.problems.append(
                    "RAM form mismatch: "
                    + self.mob.main_info[RAM_TYPE]
                    + " X "
                    + self.ram.main_info[RAM_TYPE]
                )

    def pbwatt_check(self) -> None:
        if (self.powb.is_set and self.gpu.is_set) and (
            not int(self.powb.main_info[CAPACITY][:-3])
            > int(self.gpu.main_info[INTAKE][:-3])
        ):
            self.problems.append(
                "Power block is too weak: "
                + self.powb.main_info[CAPACITY]
                + ", but needed >"
                + self.gpu.main_info[INTAKE]
            )

    def size_check(self) -> None:
        if (self.mob.is_set and self.body.is_set) and (
            not self.mob.main_info[ATX] == self.body.main_info[ATX]
        ):
            self.problems.append(
                "Form-factor mismatch: "
                + self.mob.main_info[ATX]
                + ", but body is "
                + self.body.main_info[ATX]
            )

    def check_compatibility(self) -> None:
        self.problems.clear()
        checks = [self.socket_check, self.ram_check, self.pbwatt_check, self.size_check]

        for check in checks:
            check()
