import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode #, StAggridTheme, ColumnsAutoSizeMode
# from st_aggrid.shared import JsCode




st.title('CME catalogue')

st.write('This catalogue contains coronal mass ejections (CMEs) with a speed > 1000 km/s obtained from the existing CME lists from the Large Angle and Spectrometric Coronagraph Experiment (LASCO) onboard Solar and Heliospheric Observatory (SOHO).')

df_cme_org = pd.read_csv('catalogues/SOLER_CME_catalogue.csv', sep=',',
                    parse_dates=['Start Time (Observer)', 'Start time (1 AU)', 'Start time (Sun)'])

# remove asterix (*) from columns
# for col in ['Acceleration', 'Mass', 'Kinetic Energy']:
#   df_cme_org[col] = df_cme_org[col].str.replace('*', '').astype(float)

# col1, col2, col3, col4, col5 = st.columns(5)
# sc = {}
# sc['BepiC'] = col1.checkbox("BepiColombo", value=True)
# sc['L1'] = col2.checkbox("L1 (SOHO/Wind)", value=True)
# sc['PSP'] = col3.checkbox("Parker Solar Probe", value=True)
# sc['STA'] = col4.checkbox("STEREO A", value=True)
# sc['SolO'] = col5.checkbox("Solar Orbiter", value=True)

def store_value(my_key):
    # Copy the value to the permanent key
    st.session_state[my_key] = st.session_state[f"_{my_key}"]

default_columns = df_cme_org.keys().tolist()
hid_cols = ["Start time (Sun)" , "Start time (1 AU)"]
for col in hid_cols:
  default_columns.remove(col)

if 'selected_columns_cme' in st.session_state:
  default_keys = st.session_state.selected_columns_cme
else:
  default_keys = default_columns  # TODO: provides this as an option? show all columns?

st.multiselect("Select columns to display (by default all are active).", options=df_cme_org.keys(), default=default_keys, key='_selected_columns_cme', on_change=store_value, args=["selected_columns_cme"])
# st.multiselect("Select columns to display  (by default all are active).", options=df_cme.keys(), default=df_cme.keys(), key='selected_columns_cme')
hidden_columns = df_cme_org.keys().tolist()
if 'selected_columns_cme' in st.session_state:
  df_cme = df_cme_org[st.session_state.selected_columns_cme]
  # hidden_columns = hidden_columns.remove('CME IDX')
  # st.write([col for col in st.session_state.selected_columns_cme])
  for col in st.session_state.selected_columns_cme:
    hidden_columns.remove(col) 
  # [hidden_columns.remove(col) for col in st.session_state.selected_columns_cme]
else:
  df_cme = df_cme_org[default_keys]
  for col in default_keys:
    hidden_columns.remove(col)
if len(hidden_columns) == 0:
  st.write("All columns are displayed.")
elif len(hidden_columns) > 0:
  with st.expander(f"{len(hidden_columns)} columns hidden (click for details):"):
    st.dataframe(pd.DataFrame(hidden_columns, columns=['Column name']), hide_index=True)
    st.write("To show hidden columns, select them from the multiselect box above.")

# for key, value in column.items():
#     if not value:
        # df_cme.drop(df_cme.filter(like=f'{key}_',axis=1).columns.to_list(), axis=1, inplace=True)

gb = GridOptionsBuilder.from_dataframe(df_cme)
for key in df_cme.keys():
  gb.configure_column(key, tooltipField=str(key), headerTooltip=str(key))
# gb.configure_column("flare_comments", header_name='Flare Comments', tooltipField='flare_comments', headerTooltip='Comments about flares', width=10)


# gb.configure_column("event_time", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-dd')
# gb.configure_column("event_time", type=["customDateTimeFormat"], custom_format_string='yyyy-MM-ddTHH:mm:ZZZ')

# gb.configure_pagination(enabled=True, paginationAutoPageSize=False,paginationPageSize=20)
# gb.configure_side_bar()  # TODO: not working?
# gb.configure_default_column(filter=True, groupable=True, value=True, enableRowGroup=True, aggFunc="sum")

gridOptions = gb.build()
# gridOptions['pagination'] = True
# gridOptions['paginationPageSize'] = 20    
# gridOptions['sideBar'] = True  # TODO: not working?
# gridOptions['defaultColDef'] = {"filter": True, "groupable": True, "value": True, "enableRowGroup": True, "aggFunc": "sum"}
gridOptions['rowSelection'] = 'multiple'  # 'single'
gridOptions["tooltipShowDelay"] = 500
gridOptions['toolbarPosition'] = 'bottom'
# gridOptions['suppressColumnVirtualisation'] = True
gridOptions['autoSizeStrategy'] = 'fitCellContents'

# custom_theme = (
#     StAggridTheme(base="quartz")
#     .withParams(fontSize=20)
#     .withParts("iconSetAlpine", "colorSchemeDark")
# )


grid1 = AgGrid(df_cme, show_toolbar=True, height=500, gridOptions=gridOptions, 
                updateMode=GridUpdateMode.SELECTION_CHANGED,  # GridUpdateMode.VALUE_CHANGED,
                allow_unsafe_jscode=True,
                # columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                theme=st.session_state.selected_theme,
                key="table1",
                )


if (type(grid1['selected_rows']).__name__ == "NoneType"):
  st.write('Select rows to see details!')
else:
  st.write(grid1['selected_rows'])
  # st.image(grid1['selected_rows']['IP Radio Bursts'].values[0])

st.write('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">To download a table as csv file, move the mouse over it and click on the <i class="fa-solid fa-download"></i> icon in the top right of the table.', unsafe_allow_html=True)