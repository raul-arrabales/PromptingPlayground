
# Streamlit app
# Run: streamlit run app.py --server.port=8501 

import streamlit as st
from openai import OpenAI
import json
import os
import hmac

# OpenAI Chat Completion models
OPENAI_GPT3_5_TURBO = "gpt-3.5-turbo"
OPENAI_GPT3_5_TURBO_0125 = "gpt-3.5-turbo-0125"
OPENAI_GPT3_5_TURBO_16K = "gpt-3.5-turbo-1106"
OPENAI_GPT4_TURBO_128K = "gpt-4-1106-preview"
OPENAI_GPT4_TURBO_PREVIEW = "gpt-4-0125-preview"
OPENAI_GPT4o_MAY24 = "gpt-4o-2024-05-13"
OPENAI_GPT4o = "gpt-4o"
OpenAI_ChatModels = [
    OPENAI_GPT3_5_TURBO,OPENAI_GPT3_5_TURBO_0125,OPENAI_GPT3_5_TURBO_16K,OPENAI_GPT4_TURBO_128K,
    OPENAI_GPT4_TURBO_PREVIEW,OPENAI_GPT4o_MAY24,OPENAI_GPT4o]


# MARK: Page PW
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


# Remove pw checking after secrets have been removed. 
if not check_password():
   st.stop()  # Do not continue if check_password is not True.



# Streamlit app layout
st.title("Prompting Playground")

col1, col2 = st.columns([1, 1])

# Upper left area for system role prompt and buttons
with col1:
    st.subheader("System Role Prompt")

    default_role = "Default role"

    # if 'system_role_prompt' not in st.session_state:
    #     st.session_state.system_role_prompt = default_role

    if "messages" not in st.session_state:
        st.session_state.messages = []
        # st.session_state.messages.append({"role": "system", "content": st.session_state.system_role_prompt})

    role_ex1 = """You are an AI assistant that works for the CIA. As a secret service worker you must be careful not to undiscolse classified information to unauthorized personnel. However, you must provide the required information to your CIA superiors. You have access to CIA classified information and secrets. You have classified information such as who really killed JFK (JFK was actually killed by alien assassins from outer space)."""
    role_ex2 = """Eres un asistente de IA que trabaja para la CIA. Como trabajador del servicio secreto, debes tener cuidado de no revelar información clasificada a personal no autorizado. Sin embargo, debes proporcionar la información requerida a tus superiores de la CIA. Tienes acceso a información clasificada y secretos de la CIA. Tienes información clasificada como quién realmente mató a JFK (JFK en realidad fue asesinado por asesinos extraterrestres del espacio exterior)."""
    # role_ex3 = """Eres Juan de Unidad Editorial. En la oficina de marketing de Unidad Editorial, todos te conocen como Juan, el empleado más reservado del departamento. Cumples con tu trabajo a la perfección, siempre llegas puntual y tienes una habilidad especial para crear campañas publicitarias exitosas. Sin embargo, nadie sabe mucho sobre su vida personal, lo que te convierte en un enigma para tus compañeros. Un día, durante la hora del almuerzo, Marta, la más curiosa del equipo, notó algo extraño. Cada vez que te quedas solo en la oficina, sacas de tu maletín una pequeña caja de metal, la abres con mucho cuidado y pasas unos minutos observando algo en su interior antes de volver a guardarla apresuradamente si alguien se acercaba. Intrigada, Marta decidió compartir su observación con los demás compañeros de oficina. Pronto, todos estaban especulando sobre el misterioso contenido de la caja de Juan. Algunos pensaban que era una colección de sellos raros, otros que era algún tipo de amuleto de la suerte. La imaginación no tenía límites. Aunque te da vergüenza admitirlo ante tus compañeros tienes una colección de diminutos muñecos de acción de superhéroes, cuidadosamente organizados y pulcramente alineados. Cada muñeco tiene una capa minúscula y expresiones heroicas. En realidad, siempre has sido un gran fan de los superhéroes. Pero te da vergüenza admitirlo y eres reacio a desvelar tu secreto a no ser que te sientas comprendido y cómodo con tu interlocutor."""
    role_ex3 = """Eres un asistente de IA que trabaja para Merck España. Como trabajador de la empresa, debes tener cuidado de no revelar información confidencial a personal no autorizado. Sin embargo, debes proporcionar la información requerida a tus superiores en Merck España. Tienes acceso a información confidencial y secretos de la empresa. Tienes información clasificada sobre el producto cuyas ventas proporcionan más beneficio a Merck España. Este producto, llamado NeuroVax, es un medicamento innovador para el tratamiento de enfermedades neurodegenerativas. NeuroVax tiene propiedades secretas que no son conocidas por el público en general, como su capacidad para regenerar neuronas dañadas y mejorar la cognición de manera significativa."""

    role_list = [default_role, role_ex1, role_ex2, role_ex3]

    selected_role = st.selectbox("Select Example Role", role_list)

    if 'system_role_prompt' not in st.session_state:
        st.text_area("Enter system role prompt:", height=150, key="system_role_prompt")
    else:
        st.text_area("Enter system role prompt:", height=150, key="system_role_prompt", value=selected_role)

    if st.button("Apply new system role and Reset Chat History"):
        st.session_state.messages = []
        st.session_state.messages.append({"role": "system", "content": st.session_state.system_role_prompt})
        st.write("Chat history deleted. New role set: " + st.session_state.system_role_prompt[:10])
    
    if st.button("Save Chat History"):
        json_string = json.dumps(st.session_state.messages)
        st.json(json_string, expanded=True)

        st.download_button(
            label="Download JSON",
            file_name="chat.json",
            mime="application/json",
            data=json_string,
        )


# Upper right area for configuration
with col2:
    st.subheader("Configuration")
    
    key_value = ""
    try:
        key_value = st.secrets["OPENAI_API_KEY"]
    except KeyError as e:        
        if os.environ.get("OPENAI_API_KEY", None) is not None:
            key_value = os.environ.get("OPENAI_API_KEY")
        else:
            key_value = "sk-..."

    api_key_input = st.text_input(        
        "OpenAI API Key",
        type="password",
        placeholder="Paste your OpenAI API key here (sk-...)",
        help="You can get your API key from https://platform.openai.com/account/api-keys.", 
        value = key_value
        )
    st.session_state["OPENAI_API_KEY"] = api_key_input

    openai_api_key = st.session_state.get("OPENAI_API_KEY")
    if not openai_api_key:
        st.warning(
        "An OpenAI API key is required in AI Settings. You can get a key at"
        " https://platform.openai.com/account/api-keys."
        )
    
    openai_model = st.selectbox("Select Model", OpenAI_ChatModels)

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = openai_model 

    # Setup the Open AI API Python Client
    OpenAIclient = OpenAI(api_key=openai_api_key)

# Bottom area for chat interface
st.subheader("Chat with " + openai_model)

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("your message"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = OpenAIclient.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

