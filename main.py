import streamlit as st
import streamlit.components.v1 as components

import requests
import pandas as pd

from adrubix import RubixHeatmap


# INTRO
st.set_page_config(
    page_title="AdRubix", page_icon="https://i.ibb.co/Pr9YCJk/rubik.png",
    layout="wide", initial_sidebar_state="expanded",
    menu_items={
        "About": """
        Tool for plotting complex, highly customizable heatmaps to highlight clusters in data
        and to track any patterns vis-à-vis metadata.
        
        Developed by [Alexey FEDOROV](https://github.com/afedorov-advestis)
        
        [AdRubix @ PyPI](https://pypi.org/project/adrubix/)
        
        See the complete documentation in ADRUBIX DOCS section.
        """
    }
)
st.markdown("<div id='page_top'></div>", unsafe_allow_html=True)

c1, c2, _, c3 = st.columns([1, 2, 1, 1])

with c1:
    st.markdown('<img src="https://i.ibb.co/Pr9YCJk/rubik.png" width="200"/><br/><br/>',
                unsafe_allow_html=True)

with c2:
    st.title("AdRubix × Streamlit")
    st.subheader("Streamlit GUI for AdRubix")
    st.markdown("[AdRubix @ PyPI](https://pypi.org/project/adrubix/)")

with c3:
    success = st.empty()

with st.expander("ADRUBIX DOCS"):
    resp = requests.get("https://raw.githubusercontent.com/Advestis/adrubix/master/README.md")
    readme_md = resp.text
    st.markdown(readme_md)

st.markdown("1. **Upload your files** in the sidebar")
st.markdown("2. **Set the parameters** in the sidebar (default values are preselected)")
st.markdown("3. Once all the data are uploaded, your **plot is rendered**")
st.markdown("4. Plot rendering is retriggered by modifying parameter values")
st.markdown("5. You can also retrigger it manually by pressing the button `UPDATE PLOT`")
st.markdown("6. Download the interactive HTML plot by pressing the button `DOWNLOAD HTML`")
st.markdown("7. Download the plot as a PNG image by pressing the button `DOWNLOAD PNG` "
            "(available after checking the dedicated checkbox in the sidebar)")
st.markdown("")

st.sidebar.title("AdRubix parameters")


# DATA INPUT

st.sidebar.markdown("""---""")
st.sidebar.header("Data Files")

data = None
metadata_rows = None
metadata_cols = None

data_file = st.sidebar.file_uploader("Select your MAIN DATA file")
metadata_rows_file = st.sidebar.file_uploader("Select your METADATA for ROWS file")
metadata_cols_file = st.sidebar.file_uploader("Select your METADATA for COLUMNS file")

try:
    data = pd.read_csv(data_file, header=0, index_col=0)
    with st.expander("PREVIEW MAIN DATA"):
        st.dataframe(data, height=600, width=1000)
except ValueError:
    st.warning("Please upload your main data file", icon="⚠️")

try:
    metadata_rows = pd.read_csv(metadata_rows_file, header=0, index_col=0)
    with st.expander("PREVIEW METADATA ROWS"):
        st.dataframe(metadata_rows, height=600)
except ValueError:
    st.warning("Please upload your rows metadata file", icon="⚠️")

try:
    metadata_cols = pd.read_csv(metadata_cols_file, header=0, index_col=0)
    with st.expander("PREVIEW METADATA COLUMNS"):
        st.dataframe(metadata_cols, height=600)
    st.markdown(f'<p style="text-align:right;"><a href="#plot_top">GO TO PLOT TOP</a></p>', unsafe_allow_html=True)
except ValueError:
    st.warning("Please upload your columns metadata file", icon="⚠️")

st.markdown("")
save_png = st.sidebar.checkbox("Also save plot as downloadable PNG image (will not work in the cloud)")


# DIMENSIONS

st.sidebar.markdown("""---""")
st.sidebar.header("Plot dimensions")
st.sidebar.markdown("In pixels. For one of the two, you can try setting `proportional`")

if data is not None:
    hw_default = 6 * len(data.columns)
    hh_default = 6 * len(data)
    thresh = 1.2 * hh_default
    hard_thresh = 900
    if hw_default < min(thresh, hard_thresh):
        hw_default = round(min(thresh, hard_thresh))
else:
    hw_default = 1000
    hh_default = 500

heatmap_width = st.sidebar.text_input("Main heatmap width", value=hw_default)
if heatmap_width != "proportional":
    heatmap_width = round(float(heatmap_width))

heatmap_height = st.sidebar.text_input("Main heatmap height", value=hh_default)
if heatmap_height != "proportional":
    heatmap_height = round(float(heatmap_height))

error_prop = "Upload your data first! Then you will be able to set a `proportional` width or height, if desired"
if heatmap_width == "proportional":
    if data is not None:
        heatmap_width = int(heatmap_height * len(data.columns) / len(data))
    else:
        st.error(error_prop, icon="🚨")
if heatmap_height == "proportional":
    if data is not None:
        heatmap_height = int(heatmap_width * len(data) / len(data.columns))
    else:
        st.error(error_prop, icon="🚨")


# DATAPREP

st.sidebar.markdown("""---""")
st.sidebar.header("Dataprep")

scale_along = st.sidebar.selectbox("Scale data along:", ["columns", "rows", "do not scale"], index=0)
if scale_along == "do not scale":
    scale_along = None

normalize_along = st.sidebar.selectbox("Normalize data along:", ["columns", "rows", "do not normalize"], index=2)
if normalize_along == "do not normalize":
    normalize_along = None

color_scaling_quantile = st.sidebar.slider("Color scaling quantile", min_value=80, max_value=100, value=95)

data_rows_to_drop = st.sidebar.text_input("Data rows to drop (labels separated by commas)")
data_rows_to_drop = data_rows_to_drop.split(",")
data_rows_to_drop = [row.strip() for row in data_rows_to_drop]
if data_rows_to_drop == "":
    data_rows_to_drop = None

data_cols_to_drop = st.sidebar.text_input("Data columns to drop (labels separated by commas)")
data_cols_to_drop = data_cols_to_drop.split(",")
data_cols_to_drop = [row.strip() for row in data_cols_to_drop]
if data_cols_to_drop == "":
    data_cols_to_drop = None


# COLORBAR

st.sidebar.markdown("""---""")
st.sidebar.header("Colorbar")

show_colorbar = st.sidebar.checkbox("Show colorbar", value=True)
colorbar_location = st.sidebar.radio("Colorbar location", ["top", "center", "bottom"])
colorbar_title = st.sidebar.text_input("Colorbar title")
colorbar_height = st.sidebar.number_input("Colorbar height (pixels)", value=round(hh_default / 4))
if colorbar_height == "":
    colorbar_height = None
else:
    colorbar_height = round(colorbar_height)


# METADATA & LEGENDS

st.sidebar.markdown("""---""")
st.sidebar.header("Metadata")

show_metadata_rows = st.sidebar.checkbox("Show rows metadata", value=True)
show_metadata_rows_labels = st.sidebar.checkbox("Show labels of rows metadata", value=True)
show_metadata_cols = st.sidebar.checkbox("Show columns metadata", value=True)
duplicate_metadata_cols = st.sidebar.radio(
    "Duplicate columns metadata at the bottom",
    ["no", "yes", "depending on main data size"]
)
if duplicate_metadata_cols == "depending on main data size":
    duplicate_metadata_cols = None
elif duplicate_metadata_cols == "yes":
    duplicate_metadata_cols = True
elif duplicate_metadata_cols == "no":
    duplicate_metadata_cols = False

st.sidebar.markdown("""---""")
st.sidebar.header("Legends")

show_rows_legend = st.sidebar.checkbox("Show the legend for rows metadata")
show_cols_legend = st.sidebar.checkbox("Show the legend for columns metadata", value=True)


# COLORMAPS

st.sidebar.markdown("""---""")
st.sidebar.header("Colormaps")

colormap_main = st.sidebar.text_input("Colormap for main data (known by holoviews)", value="coolwarm")
if colormap_main == "":
    colormap_main = None

colormap_metarows = st.sidebar.text_input("Colormap for rows metadata (known by holoviews)", value="glasbey")
if colormap_metarows == "":
    colormap_metarows = None

colormap_metacols = st.sidebar.text_input("Colormap for columns metadata (known by holoviews)", value="Category20")
if colormap_metacols == "":
    colormap_metacols = None

nan_color = st.sidebar.color_picker("NaN color", value="#000000")
sep_color = st.sidebar.color_picker("Color of separators", value="#ffffff")

sep_value = st.sidebar.selectbox(
    "Separators behavior",
    ["user-defined color", "min", "median", "adapt"],
)
if sep_value == "user-defined color":
    sep_value = None


# SEPARATORS & HIGHLIGHTING

st.sidebar.markdown("""---""")
st.sidebar.header("Plot enhancement")

metadata_rows_sep = st.sidebar.text_input("Rows metadata separator (column label)")
if metadata_rows_sep == "":
    metadata_rows_sep = None

metadata_cols_sep = st.sidebar.text_input("Columns metadata separator (column label)")
if metadata_cols_sep == "":
    metadata_cols_sep = None

row_labels_for_highlighting = st.sidebar.text_input("Row labels for highlighting (separated by commas)")
row_labels_for_highlighting = row_labels_for_highlighting.split(",")
row_labels_for_highlighting = [row.strip() for row in row_labels_for_highlighting]
if row_labels_for_highlighting == "":
    row_labels_for_highlighting = None


# PLOT
wrong_par_error = "WRONG PARAMETER OR DATA VALUES (please double-check and modify) ::: "

try:
    hm = RubixHeatmap(
        data=data,
        metadata_rows=metadata_rows,
        metadata_cols=metadata_cols,
        plot_save_path="./tmp.html",
        save_png=save_png,
        scale_along=scale_along,
        normalize_along=normalize_along,
        color_scaling_quantile=color_scaling_quantile,
        data_rows_to_drop=data_rows_to_drop,
        data_cols_to_drop=data_cols_to_drop,
        show_colorbar=show_colorbar,
        colorbar_location=colorbar_location,
        colorbar_title=colorbar_title,
        colorbar_height=colorbar_height,
        show_metadata_rows=show_metadata_rows,
        show_metadata_rows_labels=show_metadata_rows_labels,
        show_metadata_cols=show_metadata_cols,
        duplicate_metadata_cols=duplicate_metadata_cols,
        show_rows_legend=show_rows_legend,
        show_cols_legend=show_cols_legend,
        heatmap_width=heatmap_width,
        heatmap_height=heatmap_height,
        colormap_main=colormap_main,
        colormap_metacols=colormap_metacols,
        colormap_metarows=colormap_metarows,
        nan_color=nan_color,
        sep_color=sep_color,
        sep_value=sep_value,
        metadata_rows_sep=metadata_rows_sep,
        metadata_cols_sep=metadata_cols_sep,
        row_labels_for_highlighting=row_labels_for_highlighting
    )
except FileNotFoundError as e:
    if str(e) == "Data path is not set!":
        pass
except (KeyError, ValueError) as e:
    st.error(f"{wrong_par_error}**{str(e)}**", icon="🚨")
    st.stop()

st.markdown("<div id='plot_top'></div>", unsafe_allow_html=True)

if data is not None and metadata_rows is not None and metadata_cols is not None:

    st.markdown("""---""")
    col1, _, _, col2, _, _, col3 = st.columns(7)
    with col1:
        try:
            st.button("UPDATE PLOT", on_click=hm.plot())
        except (KeyError, ValueError) as e:
            st.error(f"{wrong_par_error}**{str(e)}**", icon="🚨")
            st.stop()
        except RuntimeError as e:
            st.error(f"WRONG RUNTIME CONFIG ::: **{str(e)}**", icon="🚨")
            st.stop()

    if save_png:
        with col2:
            try:
                with open("./tmp.png", mode='rb') as png:
                    st.download_button("DOWNLOAD PNG", data=png, file_name="heatmap.png", mime="image/x-png")
            except FileNotFoundError as e:
                st.error(f"FILE MISSING ::: {str(e)}", icon="🚨")

    try:
        with open("./tmp.html", mode='r', encoding='utf-8') as html:
            source_code = html.read().replace(
                '<body>', '<body style="background-color:white;">'
            )
        with col3:
            st.download_button("DOWNLOAD HTML", data=source_code, file_name="heatmap.html", mime="text/html")

        meta_margin_left = 50 + 72 * int(show_metadata_rows) + 150 * int(show_metadata_rows_labels)
        meta_margin_right = 180 * int(show_rows_legend) + 75 * int(show_colorbar) + 100
        html_width = meta_margin_left + heatmap_width + meta_margin_right

        meta_margin_top = 25 + 72 * int(show_metadata_cols) + 25
        meta_margin_bottom = 50 + 100 * int(duplicate_metadata_cols) + 100 * int(show_cols_legend)
        html_height = meta_margin_top + heatmap_height + meta_margin_bottom

        components.html(source_code, width=html_width, height=html_height)
        st.markdown('<p style="text-align:right;"><a href="#plot_top">BACK TO PLOT TOP</a></p>',
                    unsafe_allow_html=True)
        st.markdown('<p style="text-align:right;"><a href="#page_top">BACK TO PAGE TOP</a></p>',
                    unsafe_allow_html=True)

        success.markdown(
            '<p style="text-align:right;"><div style="color:green;font-size:20pt"><b>PLOT READY ! </b></div>' +
            '<br/><a href="#plot_top">GO TO PLOT TOP</a></p>',
            unsafe_allow_html=True
        )

    except FileNotFoundError as e:
        st.error(f"FILE MISSING: {str(e)}", icon="🚨")
