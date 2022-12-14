from __future__ import annotations
import requests as rq
import json
from bs4 import BeautifulSoup as bs
import configuration as cf
from transformers import pipeline


class Parser:

    __models: dict = {}
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

    def __init__(self):
        self.load_models()

    def load_models(self):
        if self.__models:
            return

        question_name = "deepset/roberta-base-squad2"
        self.__models["qa"] = pipeline("question-answering", model=question_name, tokenizer=question_name)
        translation_name = "Helsinki-NLP/opus-mt-ru-en"
        self.__models["trans"] = pipeline("translation", model=translation_name, tokenizer=translation_name)
        self.__models["class"] = classifier_name = "joeddav/xlm-roberta-large-xnli"
        classifier = pipeline("zero-shot-classification", model=classifier_name)

    def pages_num(self, soup: bs) -> int:
        pagination = soup.find("div", class_="PaginationWidget__wrapper-pagination")
        paginator = pagination.find_all("a")
        num = 0
        for data_page in paginator:
            if num < int(data_page["data-page"]):
                num = int(data_page["data-page"])
        return num

    def parse(self, to_file: str):
        try:
            f = open(to_file, "w")
        except IOError as e:
            return

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
            soup = bs(r.text, "html.parser")
            num = self.pages_num(soup)
            for i in range(num):
                r = rq.get(url_template + matrix[cmnt] + "?p=" + str(i + 1) + "&view_type=list")
                url_template + matrix[cmnt] + "?p=" + str(i + 1) + "&view_type=list"
                soup = bs(r.text, "html.parser")
                vacancies_names = soup.find_all(
                    "a",
                    class_="ProductCardHorizontal__title Link js--Link Link_type_default",
                )
                for name in vacancies_names:
                    cl = self.__models["class"](name.text, candidate_labels)
                    dummy = cf.PCComponent(cmnt)
                    dummy.link = "https://www.citilink.ru" + name["href"]
                    info = self.parse_info(dummy, self.get_soup(dummy))
                    namee = name.text[len(cl["labels"][0]) + 1 :]
                    data[cmnt][namee] = {
                        "link": "https://www.citilink.ru" + name["href"],
                    }
                    for key in info:
                        data[cmnt][namee][key] = info[key]

        dumped = json.dumps(data, ensure_ascii=False, indent=2)
        f.write(str(dumped))
        f.close()

    def get_soup(self, component: cf.PCComponent) -> bs:

        # print(r.status_code)
        mb_price = None
        soup = bs("")
        while not mb_price:
            r = rq.get(component.link + "properties/")
            if r.status_code != 200:
                break
            soup = bs(r.text, "html.parser")
            mb_price = soup.find("span", attrs={"itemprop": "price"})

        component.price = int(mb_price["content"])
        return soup

    def parse_info(self, subject: cf.PCComponent, soup: bs) -> dict:  # , translation: pipeline, question: pipeline

        info: dict[str, str | dict] = {}

        if soup is None:
            return info

        info[cf.PRICE] = subject.price
        info[cf.IMAGE] = soup.find(
            "img",
            class_="ProductPageStickyGallery-gallery__image-upper PreviewList__image Image",
        )["src"].title()
        specs = soup.find_all("div", class_="Specifications__row")
        out = ""
        for spec in specs:
            name = spec.find(class_="Specifications__column Specifications__column_name").contents[0].text
            value = spec.find(class_="Specifications__column Specifications__column_value").text
            out += " ".join((name + value).split()) + ";\n"

        first = out[:512].rfind(" ")
        outp = [out[:first], out[first:]]
        info[cf.ALL] = (
            self.__models["trans"](outp[0])[0]["translation_text"]
            + self.__models["trans"](outp[1])[0]["translation_text"]
        )
        out = "".join(outp)

        qdic = self.parser_matrix_qa[subject.type]
        info[cf.MAIN] = {}
        for key in qdic.keys():
            qa_input = {
                "question": self.parser_matrix_qa[subject.type][key],
                "context": out,
            }
            info[cf.MAIN][key] = self.__models["qa"](qa_input)["answer"]
        return info
