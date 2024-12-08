import streamlit as st
import webbrowser

from calculator import Structural_Model

# import constants
# from calculator import calculate
# from svg_generator import create_beam_svg

def webfelipe():
    webbrowser.open("https://felipecordero.com")

st.set_page_config(
    page_title="Concrete Retaining Wall Designer - Felipe Cordero",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': 'https://felipecordero.com',
        'Get help': "https://linkedin.com/in/felipe-cordero-osorio",
    }
)

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
# .block-container {
#     font-family: 'Helvetica', 'sans-serif';
#     font-size: 14px;
    
# }
# </style>
# """, unsafe_allow_html=True)

# st.markdown("""
# <style>
# # @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
# .block-container {
#     font-family: 'Sans', 'sans-serif';
#     font-size: 14px;
    
# }
# </style>
# """, unsafe_allow_html=True)

# # Add css to make text bigger
# st.markdown(
#     """
#     <style>
#     textarea {
#         font-size: 1rem;
#     }
#     input {
#         font-size: 1rem;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )


# Reducing whitespace on the top of the page
st.markdown("""
<style>

.block-container
{
    padding-top: 3rem;
    padding-bottom: 1rem;
    margin-top: 0rem;
}

</style>
""", unsafe_allow_html=True)

header =  st.container()
header_col1, header_col2, header_col3 = header.columns((3, 1, 0.5), vertical_alignment="center")
with header_col1:
    st.subheader("👷 Concrete Retaining Wall Designer 🛠️")
with header_col2:
    st.markdown("[**felipecordero.com**](https://felipecordero.com)")


# st.markdown("""
# <style>
# button {
#     height: 100px;
#     width: 100px;
#     color: blue;
# }
# </style>
# """, unsafe_allow_html=True)

col1, col2, col3 = st.columns([0.6, 0.5, 1.8])

# st.session_state.first_run = True

# @st.cache_data

def define_problem(*args):

    model =  Structural_Model(hd=st.session_state.hd, 
                              e=st.session_state.e, 
                              hf=st.session_state.hf, 
                              hm=st.session_state.hm, 
                            #   ka=st.session_state.ka,
                              kh=st.session_state.kh,
                            #   kae=st.session_state.kae, 
                              kv=st.session_state.kv, 
                              l1=st.session_state.l1, 
                              l2=st.session_state.l2, 
                              qsc=st.session_state.qsc, 
                              pp_tierra=st.session_state.pp_tierra, 
                              beta=st.session_state.beta, 
                              mu=st.session_state.mu,
                              phi=st.session_state.phi, 
                              fy=st.session_state.fy, 
                              fc=st.session_state.fc, 
                              rec=st.session_state.rec)

    # main drawing

    drawing.plotly_chart(model.create_drawing(), key="general_drawing")

    # Tensiones

    levante_est, levante_sis = model.get_lifting()

    levante_est = f"{round(levante_est * 100, 1)} %"
    levante_sis = f"{round(levante_sis * 100, 1)} %"

    tensiones_estaticas.write(f"Lifting = {levante_est}")
    tensiones_sismicas.write(f"Lifting = {levante_sis}")

    tensiones_estaticas.plotly_chart(model.draw_tensiones_estaticas())
    tensiones_sismicas.plotly_chart(model.draw_tensiones_sismicas())

    # Resultados generales

    general_results = list(model.get_results().items())

    string_results = ""

    for i, result in enumerate(general_results[::2], start=1):
        label, value = result
        label_2, value_2 = general_results[i * 2 - 1]
        string_results += f"""{label}: {round(value, 2)} \t {label_2}: {round(value_2, 2)}"""
        string_results += "\n"
    results.code(string_results)

    # Factores de seguridad

    strings_sf = ""

    for label, value in model.get_fs().items():
        strings_sf += f"{label}: {round(value, 2)}"
        strings_sf += "\n"
    safe_factors.code(strings_sf)

    # Resultados de Flexion en Muro

    strings_moment = ""

    for key, value in model.calcularAs().items():

        strings_moment += f"{key}  {round(value, 2)}"
        strings_moment += "\n"

    reinf_design.code(strings_moment)

    # print(st.session_state)

# # Inject custom CSS
# st.markdown("""
#     <style>
#     .stColumn { /* Adjust spacing between widgets */
#         margin-bottom: 0px;
#         margin-top: 0px;
#         padding-bottom: 0rem;
#         padding-top: 0rem;
#     }
#     </style>
#     """, unsafe_allow_html=True)

# st.markdown("""
#     <style>
#     .block-container {
#         padding-top: 1rem;
#         padding-bottom: 1rem;
#     }
#     </style>
#     """, unsafe_allow_html=True)

with col1:
    with st.container(border=True):

        st.write("**Design Parameters**")

        c1, c2 = st.columns(2, vertical_alignment="center")

        c1.text("Soil weight [ton/m³]")
        pp_tierra = c2.number_input("Peso Propio Tierra [ton/m³]:",
                                    key="pp_tierra",
                                    value=1.8, 
                                    step=0.1, 
                                    min_value=0.5, 
                                    max_value=3.5, label_visibility="collapsed",
                                    on_change=define_problem
                                    )
        
        c1, c2 = st.columns(2, vertical_alignment="center")

        c1.text("Live Load [ton/m²]")
        qsc = c2.number_input("q SC [ton/m³]: ",
                              key="qsc", 
                              value=0.5, 
                              step=0.05, 
                              min_value=0.00, 
                              max_value=10.0, label_visibility="collapsed", 
                              on_change=define_problem
                              )
        
        c1, c2 = st.columns(2, vertical_alignment="center")
        c1.text("Kh [adim]")
        kh = c2.number_input("Kh [adim]",
                             key="kh",
                             value=0.15, 
                             step=0.05, 
                             min_value=0.05, 
                             max_value=1.0, 
                             label_visibility="collapsed",
                             on_change=define_problem
                             )

        c1, c2 = st.columns(2, vertical_alignment="center")
        c1.text("Kv [adim]")
        kv = c2.number_input("Kv [adim]", 
                             key="kv",
                             value=0.08, 
                             step=0.05, 
                             min_value=0.01, 
                             max_value=0.3, 
                             label_visibility="collapsed", 
                             on_change=define_problem
                             )
        
        c1, c2 = st.columns(2, vertical_alignment="center")
        c1.text("Φ [deg]")
        phi = c2.number_input("phi [deg]: ", 
                              key="phi",
                              value=30.0, 
                              step=2.5, 
                              min_value=0.10, 
                              max_value=60.0, label_visibility="collapsed", 
                              on_change=define_problem
                              )
        
        c1, c2 = st.columns(2, vertical_alignment="center")
        c1.text("μ [adim]")
        mu = c2.number_input("mu [adim]: ",
                             key="mu", 
                             value=0.45, 
                             step=0.05, 
                             min_value=0.10, 
                             max_value=1.0, 
                             label_visibility="collapsed", 
                             on_change=define_problem
                             )
        
        # c1, c2 = st.columns(2, vertical_alignment="center")
        # c1.text("Ka [adim]")
        # ka = c2.number_input("Ka [adim]: ",
        #                      key="ka",  
        #                      value=0.30, 
        #                      step=0.05, 
        #                      min_value=0.00, 
        #                      max_value=1.0, 
        #                      label_visibility="collapsed", on_change=define_problem
        #                      )
        
        # c1, c2 = st.columns(2, vertical_alignment="center")
        # c1.text("Kae [adim]")
        # kae = c2.number_input("Kae [adim]: ", 
        #                       key="kae",  
        #                       value=0.4, 
        #                       step=0.05, 
        #                       min_value=0.00, 
        #                       max_value=1.0, label_visibility="collapsed", on_change=define_problem
        #                       )
        # c1, c2 = st.columns(2, vertical_alignment="center")
        # c1.text("Kp [adim]")
        # kp = c2.number_input("Kp [adim]: ", value=1.5, step=0.05, min_value=0.00, max_value=10.0, label_visibility="collapsed")

with col2:
    with st.container(border=True):

        st.write("**Dimensions**")

        c1, c2 = st.columns((1,1.5), vertical_alignment="center")
        c1.text("e [m]")
        e = c2.number_input("e [m]",
                            key="e",
                            value=0.2, 
                            step=0.05, 
                            min_value=0.1, 
                            max_value=1.0, 
                            label_visibility="collapsed", 
                            on_change=define_problem,
                            )
        
        c1, c2 = st.columns((1,1.5), vertical_alignment="center")
        c1.text("Hm [m]")
        hm = c2.number_input("Hm [m]", 
                             key="hm", 
                             value=2.0, 
                             step=0.05, 
                             min_value=0.5, 
                             max_value=10.0, label_visibility="collapsed", 
                             on_change=define_problem
                             )
        
        c1, c2 = st.columns((1,1.5), vertical_alignment="center")
        c1.text("Hf [m]")
        hf = c2.number_input("Hf [m]", 
                             key="hf", 
                             value=0.25, 
                             step=0.05, 
                             min_value=0.20, 
                             max_value=2.0, 
                             label_visibility="collapsed", 
                             on_change=define_problem
                             )
        
        c1, c2 = st.columns((1,1.5), vertical_alignment="center")
        c1.text("Hd [m]")
        hd = c2.number_input("Hd [m]", 
                             key="hd", 
                             value=0.00, 
                             step=0.05, 
                             min_value=0.0, 
                             max_value=5.0, 
                             label_visibility="collapsed",
                             on_change=define_problem
                             )
        
        c1, c2 = st.columns((1,1.5), vertical_alignment="center")
        c1.text("L1 [m]")
        l1 = c2.number_input("L1 [m]", 
                             key="l1", 
                             value=0.2, 
                             step=0.05, 
                             min_value=0.0, 
                             max_value=5.0, 
                             label_visibility="collapsed", 
                             on_change=define_problem
                             )
        c1, c2 = st.columns((1,1.5), vertical_alignment="center")
        c1.text("L2 [m]")
        l2 = c2.number_input("L2 [m]", 
                             key="l2", 
                             value=1.0, 
                             step=0.05, 
                             min_value=0.5, 
                             max_value=10.0, label_visibility="collapsed", 
                             on_change=define_problem
                             )
        
        c1, c2 = st.columns((1,1.5), vertical_alignment="center")
        c1.text("β [°]")
        beta = c2.number_input("beta [°]", 
                               key="beta", 
                               value=0.0, 
                               step=5., 
                               min_value=0.0, 
                               max_value=30.0, label_visibility="collapsed", 
                               on_change=define_problem
                               )

with col3:
    drawing = st.container(border=True)
    drawing.write("**Drawing**")

c1, c2 = st.columns((2, 0.33))

with c1.container(border=True):
    st.write("**Results**")
    col1, col2, col3, col4 = st.columns((0.75, 0.75, 0.8, 1.5))
    with col1:
        tensiones_estaticas =  st.container(border=True)
        tensiones_estaticas.write("**Static Presures [ton/m²]**")

    with col2:
        tensiones_sismicas = st.container(border=True)
        tensiones_sismicas.write("**Seismic + Active Presures [ton/m²]**")
    
    with col4:
        results = st.container(border=True)
        results.write("**Other Results**")


    with col3:
        safe_factors = st.container(border=True)
        safe_factors.write("**Safety Factors**")

with c2:
    reinf_design = st.container(border=True)
    reinf_design.write("**Reinforcement Moment Wall Basic Design**")

    co1, co2 = reinf_design.columns((0.6, 1.1), 
                                         vertical_alignment="center")
    
    co1.text("fy [MPa]")
    fy = co2.number_input("fy [MPa]", 
                          key="fy", 
                          value=420., 
                          step=20., 
                          min_value=280., 
                          max_value=600., 
                          label_visibility="collapsed", 
                          on_change=define_problem
                          )
    
    co1, co2 = reinf_design.columns((0.6, 1.1), vertical_alignment="center")
    co1.text("f'c [MPa]")
    fc = co2.number_input("f'c [MPa]", 
                          key="fc", 
                          value=30., 
                          step=5.0, 
                          min_value=20., 
                          max_value=50., 
                          label_visibility="collapsed", 
                          on_change=define_problem
                          )
    
    co1, co2 = reinf_design.columns((0.6, 1.1),  vertical_alignment="center")
    co1.text("rec [cm]")
    rec = co2.number_input("rec [cm]", 
                           key="rec", 
                           value=5., 
                           step=0.5, 
                           min_value=3.0, 
                           max_value=7., 
                           label_visibility="collapsed", 
                           on_change=define_problem
                           )

if header_col3.button("Calculate", type="primary"):
    define_problem()