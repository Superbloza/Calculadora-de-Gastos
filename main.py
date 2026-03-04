import streamlit as st
import math
from pathlib import Path
import streamlit.components.v1 as components

BASE_DIR = Path(__file__).resolve().parent
logo_path = BASE_DIR / "martin_prop.jpg"

# --- OTRAS FUNCIONES AUXILIARES ---

def centrar(func, *args, ancho=2, **kwargs):
    col1, col2, col3 = st.columns([1, ancho, 1])
    with col2:
        func(*args, **kwargs)

def input_con_miles(label):

    html_code = f"""
    <label style="font-family:sans-serif">{label}</label>
    
    <input id="numero" type="text"
    style="
    width:100%;
    padding:10px 12px;
    font-size:16px;
    border:1px solid #d1d5db;
    border-radius:6px;
    box-sizing:border-box;
    outline:none;
    ">
    
    <style>
    #numero:focus {{
        border-color:#ff4b4b;
        box-shadow:0 0 0 1px #ff4b4b;
    }}
    </style>
    
    <script>
    const input = document.getElementById("numero");
    
    input.addEventListener("input", function(e) {{
        let valor = input.value.replace(/\\./g,"").replace(/[^0-9]/g,"");
    
        if(valor === "") {{
            input.value = "";
            return;
        }}
    
        input.value = Number(valor).toLocaleString("es-AR");
    }});
    </script>
    """

    components.html(html_code, height=80)

# --- CONTROL DE TÉRMINOS ---
if "acepto_terminos" not in st.session_state:
    st.session_state.acepto_terminos = False

if not st.session_state.acepto_terminos:
    centrar(st.image, str(logo_path), width=150)
    st.title("Términos y Condiciones")

    st.markdown("""
    ### Aviso Legal
    
    Esta herramienta es únicamente orientativa.
    
    - Los valores son estimativos.
    - No constituyen asesoramiento legal ni impositivo.
    - Los montos definitivos dependerán de la escribanía interviniente.
    - La inmobiliaria no se responsabiliza por diferencias con el valor final de la escrituración.
    """)
    st.markdown("""
    <style>
    
    /* Aumenta tamaño */
    input[type="checkbox"] {
        transform: scale(1.3);
        accent-color: #B03A2E;   /* color del check */
    }
    
    /* Mejora el label */
    div[data-testid="stCheckbox"] label {
        font-weight: 600;
    }
    
    </style>
    """, unsafe_allow_html=True)
    if st.checkbox("Al ingresar, declaro que he leído y acepto los términos y condiciones"):
        if st.button("Ingresar a la calculadora"):
            st.session_state.acepto_terminos = True
            st.rerun()

    st.stop()

# --- LÓGICA DE CÁLCULO ---

def calcular_impuesto_sellos(localidad, valor_prop, tiene_otra_prop):
    if localidad == "Provincia":
        porc = 1.0
        return (porc * valor_prop) / 100
    else:  # CABA
        porc = 1.75
        if tiene_otra_prop == "No":  # Es vivienda única
            tope_exento = 205332000 
            if valor_prop > tope_exento:
                return (porc * (valor_prop - tope_exento)) / 100
            else:
                return 0
        return (porc * valor_prop) / 100

def calcular_agrimensor(valuacion_fiscal):
    valor_base_agrimensor = 440000
# Base: Hasta 2.000.000 vale $440.000
    if valuacion_fiscal != None:
        if valuacion_fiscal <= 2000000:
            return valor_base_agrimensor
        else:
            # De 2.000.001 en adelante
            # Restamos los 2M base y vemos cuántos "millones extra" hay
            excedente = valuacion_fiscal - 2000000
            # math.ceil redondea hacia arriba (ej: 1.2 millones cuenta como 2 adicionales)
            millones_extra = math.ceil(excedente / 1000000)
            return valor_base_agrimensor + (millones_extra * 20000)

def honorarios(rango_inicial, rango_final, step, texto, indice):
    opciones_honorarios = [x * step for x in range(rango_inicial, rango_final)]  # 0 a 4 en pasos de 0.5

    honorarios_perc = st.selectbox(
        texto,
        opciones_honorarios,
        index=indice  # 2.0% como default
        )
    return honorarios_perc
    
# --- INTERFAZ WEB ---

st.set_page_config(page_title="Simulador de Gastos", page_icon="🏠")
centrar(st.image, str(logo_path), width=320)
components.html(
    """
    <div style="
        text-align:center;
        border:1px solid #E0E0E0;
        border-radius:12px;
        padding:18px 18px 14px 18px;
        max-width:340px;
        margin: 0 auto;
        background:#FAFAFA;
        font-family: Arial, sans-serif;
    ">
      <div style="font-size:22px; font-weight:700; color:#333;">Gustavo López</div>
      <div style="font-size:13px; color:#777; margin-top:4px; margin-bottom:14px;">Asesor Inmobiliario</div>

      <div style="font-size:14px; margin-bottom:8px;">
        📞 <a style="text-decoration:none; color:#0A3D62;" target="_blank"
             href="https://wa.me/5491157610972">11-5761-0972</a>
      </div>

      <div style="font-size:14px;">
        ✉️ <a style="text-decoration:none; color:#0A3D62;"
             href="mailto:glopezinmuebles@gmail.com">glopezinmuebles@gmail.com</a>
      </div>
    </div>
    """,
    height=220,
)
st.title("Calculadora de Gastos Inmobiliarios")
st.markdown("Herramienta profesional para estimar costos de escrituración.")


# Panel lateral para valores de mercado
st.sidebar.header("Cotizaciones")
dolar_blue = st.sidebar.number_input("Dólar Blue ($)", value=1450.0, step=50.0, help="Cargue manualmente el valor del dólar blue.")

# Cuerpo principal
col1, col2 = st.columns(2)

with col1:
    localidad = st.segmented_control("Ubicación:", ["CABA", "Provincia"])
    valor_usd = input_con_miles("Ingrese el valor de la propiedad (USD)")
    if valor_usd != None:
        st.caption(f"Valor ingresado: USD {valor_usd:,.0f}".replace(",", "."))
    valor_pesos = input_con_miles("Ingrese el valor de la propiedad (ARS)")
    if valor_pesos != None:
        st.caption(f"Valor ingresado: ARS {valor_pesos:,.0f}".replace(",", "."))

with col2:
    rol = st.segmented_control("Tu rol:", ["Comprador", "Vendedor"])
    hon_inmo = 0.0
    hon_escr = 0.0
    if rol == "Comprador":
        hon_inmo = honorarios(0, 9, 0.5, "% Honorarios Inmobiliaria:", 8)  # Rango 0-4% en pasos de 0.5
        hon_escr = honorarios(0, 5, 0.5, "% Honorarios Escribanía:", 4)  # Rango 0-2% en pasos de 0.5
    else:
        hon_inmo = honorarios(0, 7, 0.5, "% Honorarios Inmobiliaria:", 6)  # Rango 0-4% en pasos de 0.5

# Lógica condicional para vivienda única
tiene_otra = "Sí"
if localidad == "CABA":
    if rol == "Comprador":
        pregunta = "¿Posee otra propiedad en CABA?"
    else:
        pregunta = "¿El comprador posee otra propiedad en CABA?"
    tiene_otra = st.radio(pregunta, ["Sí", "No"], help="Seleccione 'No' si es vivienda única para aplicar exenciones.")
        
tiene_sup_desc = "No"
if localidad == "Provincia" and rol == "Vendedor":
    pregunta2 = "¿La propiedad tiene superficie descubierta?"
    tiene_sup_desc = st.radio(pregunta2, ["Sí", "No"], help="En caso de tener superficie descubierta, agrega el valor del agrimensor.")
    
valuacion_fiscal = 0.0
if tiene_sup_desc == "Sí":
    valuacion_fiscal = input_con_miles("Ingrese la valuación fiscal (ARS)")
    if valuacion_fiscal != None:
        st.caption(f"Valor ingresado: ARS {valuacion_fiscal:,.0f}".replace(",", "."))
    
# Condición: Vendedor + Provincia + Superficie descubierta
costo_agrimensor = 0.0
if rol == "Vendedor" and localidad == "Provincia" and tiene_sup_desc == "Sí" and valuacion_fiscal != None:
    costo_agrimensor = calcular_agrimensor(valuacion_fiscal)
    st.warning(f"Se debe realizar estado parcelario. Costo Agrimensor Estimado: ${costo_agrimensor:,.0f}")

if rol in ["Comprador", "Vendedor"] and localidad in ["CABA", "Provincia"]:
    # Botón de cálculo
        if st.button("Calcular Gastos Ahora"):
            if valor_usd == None or valor_pesos == None or valuacion_fiscal == None:
                st.info("Por favor, complete los campos para calcular los gastos estimados.")
                st.stop()
            else:
                # Cálculos
                sellos = calcular_impuesto_sellos(localidad, valor_pesos, tiene_otra)
                aporte = (0.2 * valor_pesos) / 100
                otros = (0.8 * valor_pesos) / 100
                gastos_pesos = sellos + aporte + otros
                if localidad == "Provincia" and rol == "Vendedor" and tiene_sup_desc == "Sí":
                    gastos_pesos += costo_agrimensor
                
                honorarios_inmobiliaria = valor_usd * (hon_inmo / 100)
                honorarios_escribania = valor_usd * (hon_escr / 100)
                
                
                st.divider()
                st.subheader("Resumen Estimado")
                
                if sellos == 0:
                    st.info("No se aplicó Impuesto de Sellos por ser vivienda única en CABA.")
                
                if costo_agrimensor > 0:
                    c1, c2, c3, c4 = st.columns(4)
                    c4.metric("Costo Agrimensor", f"${costo_agrimensor:,.0f}")
                else:
                    c1, c2, c3 = st.columns(3)
                    
                c1.metric("Imp. Sellos", f"${sellos:,.0f}")
                c2.metric("Aporte Notarial", f"${aporte:,.0f}")
                c3.metric("Otros Gastos", f"${otros:,.0f}")
                
                st.success(f"### Gastos en Pesos: ${gastos_pesos:,.2f} ARS")
                c1, c2 = st.columns(2)
                with c1:
                    c1.metric("Honorarios Inmobiliaria", f"${honorarios_inmobiliaria:,.2f} USD")
                    gastos_pesos_convertidos_blue = gastos_pesos / dolar_blue
                    c1.metric("Gastos en Pesos Convertidos a USD (Dólar Blue):", f"${gastos_pesos_convertidos_blue:,.2f} USD")
                with c2:
                    if rol == "Comprador":
                        c2.metric("Honorarios Escribanía", f"${honorarios_escribania:,.2f} USD")
                gastos_totales_a_abonar_en_dolares = honorarios_inmobiliaria + honorarios_escribania + gastos_pesos_convertidos_blue
                st.success(f"### Total a Abonar en USD (Dólar Blue): ${gastos_totales_a_abonar_en_dolares:,.2f} USD")

                st.caption("Nota: Los valores son orientativos basados en la normativa vigente y al solo efecto de orientar con los gastos al cliente. Los valores definitivos dependerán de la proforma de la escribanía interviniente.")















