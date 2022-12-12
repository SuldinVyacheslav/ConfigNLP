from transformers import pipeline

# sys.path is a list of absolute path strings
import sys
from os.path import dirname, abspath

sys.path.append(dirname(dirname(abspath(__file__))) + "/src")
import app.parser as ps
import app.configuration as cf

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

question_name = "deepset/roberta-base-squad2"
translation_name = "Helsinki-NLP/opus-mt-ru-en"
models = {
    "translation_model": pipeline(
        "translation", model=translation_name, tokenizer=translation_name
    ),
    "q_a_model": pipeline(
        "question-answering", model=question_name, tokenizer=question_name
    ),
}


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
    f = open("samples/mb.json", "r")
    ps.parse_info(
        cfg.mob,
        bs(f.read(), "html.parser"),
        models["translation_model"],
        models["q_a_model"],
    )
    for key in right_parsed_mb:
        assert cfg.mob.main_info[key] == right_parsed_mb[key]


def test_parser_cpu() -> None:
    right_parsed_cpu = {
        cf.CPU_SOCKET: "LGA 1200",
        cf.FREQUENCY: "2.9",
        cf.HEAT_OUT: "65 Вт",
    }
    f = open("samples/cpu.json", "r")
    ps.parse_info(
        cfg.cpu,
        bs(f.read(), "html.parser"),
        models["translation_model"],
        models["q_a_model"],
    )
    for key in right_parsed_cpu:
        assert cfg.cpu.main_info[key] == right_parsed_cpu[key]


def test_parser_ram() -> None:
    right_parsed = {
        cf.DDR: "DDR4",
        cf.FREQUENCY: "2666МГц",
        cf.CAPACITY: "8 ГБ",
        cf.RAM_TYPE: "DIMM",
    }
    f = open("samples/ram.json", "r")
    ps.parse_info(
        cfg.ram,
        bs(f.read(), "html.parser"),
        models["translation_model"],
        models["q_a_model"],
    )
    for key in right_parsed:
        print(cfg.ram.main_info[key])
        assert cfg.ram.main_info[key] == right_parsed[key]


def test_parser_gpu() -> None:
    right_parsed = {cf.DDR: "GDDR6", cf.INTAKE: "500 Вт", cf.SLOT: "PCI-E 4.0"}
    f = open("samples/gpu.json", "r")
    ps.parse_info(
        cfg.gpu,
        bs(f.read(), "html.parser"),
        models["translation_model"],
        models["q_a_model"],
    )
    for key in right_parsed:
        print(cfg.gpu.main_info[key])
        assert cfg.gpu.main_info[key] == right_parsed[key]


def test_parser_pb() -> None:
    right_parsed = {cf.CAPACITY: "750 Вт", cf.LENGTH: "140"}
    f = open("samples/pb.json", "r")
    ps.parse_info(
        cfg.powb,
        bs(f.read(), "html.parser"),
        models["translation_model"],
        models["q_a_model"],
    )
    for key in right_parsed:
        print(cfg.powb.main_info[key])
        assert cfg.powb.main_info[key] == right_parsed[key]


def test_parser_body() -> None:
    right_parsed = {cf.ATX: "miniITX"}
    f = open("samples/body.json", "r")
    ps.parse_info(
        cfg.body,
        bs(f.read(), "html.parser"),
        models["translation_model"],
        models["q_a_model"],
    )
    for key in right_parsed:
        print(cfg.body.main_info[key])
        assert cfg.body.main_info[key] == right_parsed[key]
