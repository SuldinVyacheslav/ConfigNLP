from __future__ import annotations
import requests as rq
import json
from bs4 import BeautifulSoup as bs
import configuration as cf
from transformers import pipeline

question_name = "deepset/roberta-base-squad2"
question_model = pipeline(
    "question-answering", model=question_name, tokenizer=question_name
)


translation_name = "Helsinki-NLP/opus-mt-ru-en"
translation_model = pipeline(
    "translation", model=translation_name, tokenizer=translation_name
)


def pages_num(soup: bs) -> int:
    pagination = soup.find("div", class_="PaginationWidget__wrapper-pagination")
    paginator = pagination.find_all("a")
    num = 0
    for data_page in paginator:
        if num < int(data_page["data-page"]):
            num = int(data_page["data-page"])
    return num


def parce(to_file: str) -> None:
    try:
        f = open(to_file, "w")
    except IOError as e:
        return None

    classifier_name = "joeddav/xlm-roberta-large-xnli"
    classifier = pipeline("zero-shot-classification", model=classifier_name)
    data: dict[str, dict[str, dict]] = {}

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
        data[cmnt] = {}
        r = rq.get(url_template + matrix[cmnt], allow_redirects=True)
        print(r.status_code, r.url)
        soup = bs(r.text, "html.parser")
        num = pages_num(soup)
        for i in range(2):  # range(num):
            r = rq.get(
                url_template + matrix[cmnt] + "?p=" + str(i + 1) + "&view_type=list"
            )
            print(r.status_code)
            print(r.url)
            url_template + matrix[cmnt] + "?p=" + str(i + 1) + "&view_type=list"
            soup = bs(r.text, "html.parser")
            vacancies_names = soup.find_all(
                "a",
                class_="ProductCardHorizontal__title Link js--Link Link_type_default",
            )
            print("*" * 90)
            i = 0
            for name in vacancies_names:
                cl = classifier(name.text, candidate_labels)
                dummy = cf.PCComponent(cmnt)
                dummy.link = "https://www.citilink.ru" + name["href"]
                info = parse_info(dummy, get_soup(dummy))
                namee = name.text[len(cl["labels"][0]) + 1 :]
                data[cmnt][namee] = {
                    "link": "https://www.citilink.ru" + name["href"],
                }
                for key in info:
                    data[cmnt][namee][key] = info[key]
                i += 1
                print(namee)
                if i == 2:
                    break

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


def get_soup(component: cf.PCComponent) -> bs:

    # print(r.status_code)
    mb_price = None
    soup = bs("")
    while not mb_price:
        r = rq.get(component.link + "properties/")
        print(r.status_code)
        if r.status_code != 200:
            break
        soup = bs(r.text, "html.parser")
        mb_price = soup.find("span", attrs={"itemprop": "price"})

    component.price = int(mb_price["content"])
    return soup


def parse_info(
    subject: cf.PCComponent, soup: bs  # , translation: pipeline, question: pipeline
) -> dict:

    info = {}

    if soup is None:
        return info

    info[cf.PRICE] = subject.price
    info[cf.IMAGE] = soup.find(
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
    info[cf.ALL] = (
        translation_model(outp[0])[0]["translation_text"]
        + translation_model(outp[1])[0]["translation_text"]
    )
    out = "".join(outp)

    qdic = parser_matrix_qa[subject.type]
    info[cf.MAIN] = {}
    for key in qdic.keys():

        qa_input = {"question": parser_matrix_qa[subject.type][key], "context": out}
        info[cf.MAIN][key] = question_model(qa_input)["answer"]
    return info
    # subject.is_set = True


# r = requests.get("https://www.citilink.ru/catalog/materinskie-platy/")
# print(r.status_code)
# parce("info.json")

# cmnt = cf.MB
# dummy = cf.PCComponent(cmnt)
# dummy.link = "https://www.citilink.ru/product/materinskaya-plata-asrock-h610m-hdv-m-2-soc-1700-intel-h610-2xddr4-atx-1680404/"
# info = parse_info(dummy, get_soup(dummy))
# import pprint
# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(info)
