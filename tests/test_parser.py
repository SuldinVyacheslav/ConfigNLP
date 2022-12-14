import os

from transformers import pipeline

import src.parser as ps
import src.configuration as cf

from bs4 import BeautifulSoup as bs


#
# # setup
cfg = cf.Configuration("test")
cfg.mob = cf.MotherBoard("Motherboard")
cfg.ram = cf.RAMemory("RAM")
cfg.cpu = cf.Procesor("Processor")
cfg.gpu = cf.VideoCard("Video Card")
cfg.powb = cf.PowerBlock("Power Block")
cfg.body = cf.Body("Body")

test_html = {
    "Motherboard": "samples/mb.json",
    "Processor": "samples/cpu.json",
    "Video Card": "samples/gpu.json",
    "RAM": "samples/ram.json",
    "Power Block": "samples/pb.json",
    "Body": "samples/body.json",
}

parser = ps.Parser()

def test_parser_motherboard() -> None:
    # assert 1 == 1, "EYA"
    right_parsed_mb = {
        cf.CHIPSET: "Intel H470",
        cf.SOCKET: "LGA 1200",
        cf.DDR: "DDR4 2",
        cf.RAM_TYPE: "DIMM",
        cf.FREQUENCY: "2933 МГц",
        cf.ATX: "mATX",
    }
    f = open(os.path.join(os.getcwd(), "tests/samples/mb.json"), "r")
    info = parser.parse_info(cfg.mob, bs(f.read(), "html.parser"))
    for key in right_parsed_mb:
        assert info[cf.MAIN][key] == right_parsed_mb[key]


def test_parser_cpu() -> None:
    right_parsed_cpu = {
        cf.CPU_SOCKET: "LGA 1200",
        cf.FREQUENCY: "2.9",
        cf.HEAT_OUT: "65 Вт",
    }
    f = open(os.path.join(os.getcwd(), "tests/samples/cpu.json"), "r")
    info = parser.parse_info(cfg.cpu, bs(f.read(), "html.parser"))
    for key in right_parsed_cpu:
        assert info[cf.MAIN][key] == right_parsed_cpu[key]


def test_parser_ram() -> None:
    right_parsed = {
        cf.DDR: "DDR4",
        cf.FREQUENCY: "2666МГц",
        cf.CAPACITY: "8 ГБ",
        cf.RAM_TYPE: "DIMM",
    }
    f = open(os.path.join(os.getcwd(), "tests/samples/ram.json"), "r")
    info = parser.parse_info(cfg.ram, bs(f.read(), "html.parser"))
    for key in right_parsed:
        print(cfg.ram.main_info[key])
        assert info[cf.MAIN][key] == right_parsed[key]


def test_parser_gpu() -> None:
    right_parsed = {cf.DDR: "GDDR6", cf.INTAKE: "500 Вт", cf.SLOT: "PCI-E 4.0"}
    f = open(os.path.join(os.getcwd(), "tests/samples/gpu.json"), "r")
    info = parser.parse_info(cfg.gpu, bs(f.read(), "html.parser"))
    for key in right_parsed:
        print(cfg.gpu.main_info[key])
        assert info[cf.MAIN][key] == right_parsed[key]


def test_parser_pb() -> None:
    right_parsed = {cf.CAPACITY: "750 Вт", cf.LENGTH: "140"}
    f = open(os.path.join(os.getcwd(), "tests/samples/pb.json"), "r")
    info = parser.parse_info(cfg.powb, bs(f.read(), "html.parser"))
    for key in right_parsed:
        print(cfg.powb.main_info[key])
        assert info[cf.MAIN][key] == right_parsed[key]


def test_parser_body() -> None:
    right_parsed = {cf.ATX: "miniITX"}
    f = open(os.path.join(os.getcwd(), "tests/samples/body.json"), "r")
    info = parser.parse_info(cfg.body, bs(f.read(), "html.parser"))
    for key in right_parsed:
        print(cfg.body.main_info[key])
        assert info[cf.MAIN][key] == right_parsed[key]