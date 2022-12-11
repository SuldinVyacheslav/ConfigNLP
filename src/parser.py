from __future__ import annotations

import typing

import requests as rq
import json
from bs4 import BeautifulSoup as bs
import configuration as cf
from transformers import pipeline


def pages_num(soup: bs) -> int:
    pagination = soup.find("div", class_="PaginationWidget__wrapper-pagination")
    paginator = pagination.find_all("a")
    num = 0
    for data_page in paginator:
        if num < int(data_page["data-page"]):
            num = int(data_page["data-page"])
    return num


def parce(to_file: str, classifier: pipeline) -> None:

    data: dict[str, list[str | typing.Any]] = {}

    candidate_labels = [
        "Модуль памяти",
        "Видеокарта",
        "Процессор",
        "Материнская плата",
        "Блок питания",
        "Корпус",
    ]

    url_template = "https://www.citilink.ru/catalog/"
    matrix = {
        cf.MB: "materinskie-platy/",
        cf.CPU: "processory/",
        cf.GPU: "videokarty/",
        cf.RAM: "moduli-pamyati/",
        cf.PB: "bloki-pitaniya/",
        cf.BODY: "korpusa/",
    }
    for cmnt in matrix.keys():
        data[cmnt] = []
        r = rq.get(url_template + matrix[cmnt], allow_redirects=True)
        soup = bs(r.text, "html.parser")
        num = pages_num(soup)
        for i in range(num):
            r = rq.get(
                url_template + matrix[cmnt] + "?p=" + str(i + 1) + "&view_type=list"
            )
            url_template + matrix[cmnt] + "?p=" + str(i + 1) + "&view_type=list"
            soup = bs(r.text, "html.parser")
            vacancies_names = soup.find_all(
                "a",
                class_="ProductCardHorizontal__title Link js--Link Link_type_default",
            )
            for name in vacancies_names:
                cl = classifier(name.text, candidate_labels)
                data[cmnt].append(
                    {
                        "name": name.text[len(cl["labels"][0]) + 1 :],
                        "link": "https://www.citilink.ru" + name["href"],
                    }
                )
    f = open(to_file, "w")
    dumped = json.dumps(data, ensure_ascii=False, indent=2)
    f.write(str(dumped))
    f.close()


parser_matrix_qa = {
    cf.MB: {
        cf.CHIPSET: "Какой Чипсет?",
        cf.SOCKET: "Какое Гнездо процессора?",
        cf.ATX: "Какой Форм-фактор?",
        cf.DDR: "DDR?",
        cf.RAM_TYPE: "Тип поддерживаемой памяти ?",
        cf.FREQUENCY: "Частотная спецификация памяти?",
    },
    cf.CPU: {
        cf.SOCKET: "Какое Гнездо процессора?",
        cf.FREQUENCY: "Частота:?",
        cf.HEAT_OUT: "Тепловыделение?",
    },
    cf.RAM: {
        cf.DDR: "Тип памяти",
        cf.FREQUENCY: "Скорость?",
        cf.CAPACITY: "Объем модуля?",
        cf.RAM_TYPE: "Форм-фактор ?",
    },
    cf.GPU: {
        cf.DDR: "Тип видеопамяти?",
        cf.INTAKE: "Рекомендуемая мощность БП?",
        cf.SLOT: "Интерфейс?",
    },
    cf.PB: {cf.CAPACITY: "Мощность?", cf.LENGTH: "Размеры (ШхВхГ) ?"},
    cf.BODY: {cf.ATX: "Какой Форм-фактор?"},
}


def get_soup(component: cf.PCComponent) -> bs | None:

    # print(r.status_code)
    mb_price = None
    soup = None
    while not mb_price:
        r = rq.get(component.link + "properties/")
        if r.status_code != 200:
            return None
        soup = bs(r.text, "html.parser")
        mb_price = soup.find("span", attrs={"itemprop": "price"})

    component.price = int(mb_price["content"])
    return soup


def parse_info(
    subject: cf.PCComponent, soup: bs, translation: pipeline, question: pipeline
) -> None:

    if soup is None:
        return None

    subject.image = soup.find(
        "img",
        class_="ProductPageStickyGallery-gallery__image-upper PreviewList__image Image",
    )["src"]
    specs = soup.find_all("div", class_="Specifications__row")
    out = ""
    for spec in specs:
        name = (
            spec.find(class_="Specifications__column Specifications__column_name")
            .contents[0]
            .text
        )
        value = spec.find(
            class_="Specifications__column Specifications__column_value"
        ).text
        out += " ".join((name + value).split()) + ";\n"

    first = out[:512].rfind(" ")
    outp = [out[:first], out[first:]]
    subject.all_info = (
        translation(outp[0])[0]["translation_text"]
        + translation(outp[1])[0]["translation_text"]
    )
    out = "".join(outp)

    qdic = parser_matrix_qa[subject.type]
    for key in qdic.keys():

        qa_input = {"question": parser_matrix_qa[subject.type][key], "context": out}
        subject.main_info[key] = question(qa_input)["answer"]
    subject.is_set = True
