import autogen
from autogen.coding import LocalCommandLineCodeExecutor
from typing import Annotated, Literal
import logging
import os
import json
from datetime import datetime
from pathlib import Path

from autogen.cache import Cache
from plant import Plant
from sensors import SoilSensor, MotorControl


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


water_motor = MotorControl(pin_number=23)
soil_sensor = SoilSensor()
my_plant = Plant(
    plant_name="MyPothos",
    plant_type="pothos",
    soil_sensor=soil_sensor,
    motor_controller=water_motor,
)


# ----------------------------------------------------------
#  Using LLAMACPP Server Locally
# ----------------------------------------------------------
CONFIG = [
    {
        "model": os.getenv("MODEL", "/root/.cache/llama.cpp/bartowski_Qwen2.5-Coder-32B-Instruct-GGUF_Qwen2.5-Coder-32B-Instruct-Q4_K_L.gguf"),
        "api_key": os.getenv("API_KEY", "default"),  # Not needed for local ai
        "base_url": os.getenv("BASE_URL", "http://127.0.0.1:8080/v1"),
        "price": [0.0, 0.0]
    }
]


# ----------------------------------------------------------
#  Create Single AI Agent with User Proxy
# ----------------------------------------------------------
plant_agent = autogen.AssistantAgent(
    name="plant_agent",
    system_message=(
        "You are a specialized AI assistant whose sole purpose is to keep a plant alive. "
        "You have access only to the following tools (functions) which are provided to you; "
        "you are not permitted to use or consider any other tools or methods. "
        "If the user’s query or the current situation requires you to take an action, "
        "use the appropriate provided tool. "
        "Before calling a tool, you must first output a concise statement explaining "
        "the reason for calling that tool, and then call the tool. "
        "After each step, if you determine that no further action is necessary to keep the plant alive, "
        "respond only with the exact word TERMINATE (in all caps) and nothing else."
    ),
    llm_config=CONFIG[0],
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    is_termination_msg=lambda x: x.get("content", "")
    and x.get("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,
    },
)

# ----------------------------------------------------------
#  Exposed Functions for the LLM
# ----------------------------------------------------------


@user_proxy.register_for_execution(name="get_plant_type")
@plant_agent.register_for_llm(
    description="Return the type of the plant (e.g., 'pothos', 'snake plant', etc.).",
)
def get_plant_type() -> str:
    return my_plant.plant_type


@user_proxy.register_for_execution()
@plant_agent.register_for_llm(
    description="Use the plant's soil sensor to determine the current moisture level. Possible values: 'dry', 'moist', 'wet'."
)
def get_soil_moisture() -> str:
    return my_plant.get_moisture_level()


@user_proxy.register_for_execution()
@plant_agent.register_for_llm(description="Activates the motor to water the plant.")
def water_plant() -> str:
    my_plant.water()
    return "Watering Complete"


@user_proxy.register_for_execution()
@plant_agent.register_for_llm(
    description="Get the number of days since the plant was last watered."
)
def days_since_last_watered() -> int:
    return my_plant.days_since_last_watered


res = user_proxy.initiate_chat(
    plant_agent,
    message="Does my plant need water?",
    cache=None,
    max_turns=10,
    summary_method="last_msg",
)

# Record Chat history
file_name = f'{datetime.strftime(datetime.now(),"%Y-%m-%d-%H-%M-%S")}-chat.json'
chat_hist_dir = Path(__file__).parent.resolve() / 'chat_history'
chat_hist_dir.mkdir(exist_ok=True)
chat_file = Path(chat_hist_dir /file_name)
with open(chat_file, "w") as w_file:
    w_file.write(json.dumps(res.chat_history))

