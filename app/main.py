import json
import os

from pathlib import Path

import streamlit as st


import src.configuration as cf


def main_widgets():
    with st.sidebar:
        for cmnt in st.session_state.data.keys():
            add_selectbox = st.sidebar.selectbox(
                cmnt,
                [""] + [key for key in st.session_state.data[cmnt]],
                key=cmnt,
                on_change=add,
                args=(cmnt,),
            )
    newConfig = st.button("New configuration")

    if newConfig:
        st.session_state.configs.clear()
        st.session_state.configs.append(cf.Configuration("1"))


def layout():
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
    with open(os.path.join(os.getcwd(), "css/style.css")) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.markdown(
        Path(os.path.join(os.getcwd(), "css/header.md")).read_text(),
        unsafe_allow_html=True,
    )


def session():
    if "configs" not in st.session_state:
        st.session_state["configs"] = []

    if "data" not in st.session_state:
        with open(os.path.join(os.getcwd(), "data/info.json")) as f:
            st.session_state["data"] = json.loads(f.read())


def main():
    layout()
    session()
    main_widgets()
    show_all()


def show_component(component: cf.PCComponent):
    main, image = st.columns([3, 1])
    if component.name:
        with main:
            st.write("✅ " + f"[{component.name}]({component.link})")
            with st.expander("Details"):
                for position in component.all_info.split(";"):
                    st.markdown(position)
                st.markdown("### COST: " + str(component.price) + "₽")
        with image:
            if component.image:
                st.image(component.image)


def show_all():
    for config in st.session_state.configs:
        mb, cpu, gpu, ram, powbl, bodu = st.tabs([cf.MB, cf.CPU, cf.GPU, cf.RAM, cf.PB, cf.BODY])
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


def add(component_type: str):
    if not len(st.session_state.configs):
        st.warning("⚠️ So far, you have not created an assembly. You can do this using the button below")
        return
    cur = st.session_state.configs[0]
    call: dict[str, cf.PCComponent] = {
        cf.MB: cur.mob,
        cf.CPU: cur.cpu,
        cf.GPU: cur.gpu,
        cf.RAM: cur.ram,
        cf.PB: cur.powb,
        cf.BODY: cur.body,
    }

    component_name: str = st.session_state[component_type]
    component = call[component_type]
    component_data = st.session_state.data[component_type][component_name]

    # mapping
    component.link = component_data[cf.LINK]
    component.price = component_data[cf.PRICE]
    component.name = component_name
    component.main_info = component_data[cf.MAIN]
    component.image = component_data[cf.IMAGE]
    component.all_info = component_data[cf.ALL]
    component.is_set = True

    st.session_state[component_type] = ""


if __name__ == "__main__":
    main()
