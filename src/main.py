import json
from parser import parse_info, get_soup
import streamlit as st
import configuration as cf
from pathlib import Path
from transformers import pipeline

import sys


st.set_page_config(
    page_title="MyConfig",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "Get Help": "https://t.me/SuldinVyacheslav",
        "Report a bug": "https://t.me/SuldinVyacheslav",
        "About": "todo =)",
    },
)

sys.path
sys.path.append('/app/confignlp/src')
print(sys.path)
st.markdown(Path("file.md").read_text(), unsafe_allow_html=True)

if "models" not in st.session_state:
    question_name = "deepset/roberta-base-squad2"
    question = pipeline(
        "question-answering", model=question_name, tokenizer=question_name
    )

    classifier_name = "joeddav/xlm-roberta-large-xnli"
    classifier = pipeline("zero-shot-classification", model=classifier_name)

    translation_name = "Helsinki-NLP/opus-mt-ru-en"
    translation = pipeline(
        "translation", model=translation_name, tokenizer=translation_name
    )

    st.session_state["models"] = {
        "translation_model": translation,
        "classifier_model": classifier,
        "q_a_model": question,
    }


if "configs" not in st.session_state:
    st.session_state["configs"] = []


def read_data(filename: str) -> dict:
    f = open(filename)
    r = json.loads(f.read())
    f.close()
    return r


if "data" not in st.session_state:
    st.session_state["data"] = read_data("data.json")
    st.session_state["data_names"] = {}
    for key in st.session_state["data"].keys():
        names = []
        for pair in st.session_state["data"][key]:
            names.append(pair["name"])
        st.session_state["data_names"][key] = names


# def resolve_search(key, subject, containter):
#
#     if st.session_state[key] == "ASUS":
#         subject.name = "ASUS ROG STRSSSIX"
#         containter.success(subject.type + " successfully founded!", icon="✅")
#         st.session_state["configs"][0].check_compatibility()
#     else:
#         containter.error(
#             "Cant find. Try enter in side bar or recheck entered value", icon="❌"
#         )
#     st.session_state[key] = ""


def show_component(component: cf.PCComponent) -> None:
    main, image = st.columns([3, 1])
    # containter.text_input(
    #     label="Lets find your " + subject.type + "! =)",
    #     max_chars=64,
    #     key=key,
    #     on_change=resolve_search,
    #     args=(key, subject, containter),
    # )
    if component.name:
        with main:
            st.write("✅ " + component.name)
            with st.expander("Details"):
                st.write(component.main_info.values())
                for position in component.all_info.split(";"):
                    st.markdown(position)
                st.markdown("### COST: " + str(component.price) + "₽")
        with image:
            if component.image:
                st.image(component.image)


def show_all() -> None:
    for config in st.session_state.configs:
        mb, cpu, gpu, ram, powbl, bodu = st.tabs(
            [cf.MB, cf.CPU, cf.GPU, cf.RAM, cf.PB, cf.BODY]
        )
        with mb:
            show_component(config.mob)
        with cpu:
            show_component(config.cpu)
        with gpu:
            show_component(config.gpu)
        with ram:
            show_component(config.ram)
        with powbl:
            show_component(config.powb)
        with bodu:
            show_component(config.body)

        st.session_state.configs[0].check_compatibility()
        for error in st.session_state.configs[0].problems:
            st.error("❌ Compatability error: " + error)
        st.write(
            """<font size="7">"""
            + "Summary cost: "
            + str(st.session_state.configs[0].get_price())
            + " ₽"
            + """</font>""",
            unsafe_allow_html=True,
        )


def add(component_type: str) -> None:
    if not len(st.session_state.configs):
        st.warning(
            "⚠️ So far, you have not created an assembly. You can do this using the button below"
        )
        return
    cur = st.session_state.configs[0]
    call = {
        cf.MB: cur.mob,
        cf.CPU: cur.cpu,
        cf.GPU: cur.gpu,
        cf.RAM: cur.ram,
        cf.PB: cur.powb,
        cf.BODY: cur.body,
    }
    call[component_type].name = st.session_state[component_type]
    sub = call[component_type]
    call[component_type].link = st.session_state.data[component_type][
        st.session_state.data_names[component_type].index(
            st.session_state[component_type]
        )
    ]["link"]
    if (
        parse_info(
            sub,
            get_soup(sub),
            st.session_state.models["translation_model"],
            st.session_state.models["q_a_model"],
        )
        is None
    ):
        call[component_type].name = ""
        st.error("🚫 Seems like 429 code - permission denied, try later!")

    st.session_state[component_type] = ""


with st.sidebar:
    data = st.session_state.data_names
    for cmnt in data.keys():
        add_selectbox = st.sidebar.selectbox(
            cmnt,
            [""] + st.session_state.data_names[cmnt],
            key=cmnt,
            on_change=add,
            args=(cmnt,),
        )

if __name__ == "__main__":

    newConfig = st.button("New configuration")

    if newConfig:
        st.session_state.configs.clear()
        st.session_state.configs.append(cf.Configuration("1"))
    show_all()


with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
