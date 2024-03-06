#streamit_helper.py
import logging
import time

import streamlit as st
from streamlit.logger import get_logger


class StreamlitObject:
    def __init__(self):
        self.component = st.empty()


class StreamlitLogHandler(logging.Handler):
    def __init__(self, component):
        super().__init__()
        self.component = component

    def emit(self, record):
        msg = self.format(record)
        self.component = st.empty()
        self.component.text(msg)


streamlit_logger = get_logger(__name__)
st_obj = StreamlitObject()
streamlit_handler = StreamlitLogHandler(st_obj)
streamlit_logger.addHandler(streamlit_handler)
