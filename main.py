import autogen
from autogen.coding import LocalCommandLineCodeExecutor
from typing import Annotated, Literal
import logging
import os
from datetime import datetime

from autogen.cache import Cache
from plant import Plant
from sensors import SoilSensor, MotorControl


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


water_motor = MotorControl(pin_number=18)
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
        "model": os.getenv("MODEL", "Mistral-Small-24B-Instruct-2501-Q6"),
        "api_key": os.getenv("API_KEY", "default"),  # Not needed for local ai
        "base_url": os.getenv("BASE_URL", "http://192.168.1.16:8080/v1"),
    }
]


# ----------------------------------------------------------
#  Create Single AI Agent with User Proxy
# ----------------------------------------------------------
plant_agent = autogen.AssistantAgent(
    name="plant_agent",
    system_message=(
        "Use only the functions provided to keep the plant "
        f"alive and in good health. Today's date is {datetime.now()} "
        "Reply TERMINATE when the task is done."
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
    name="get_plant_type",
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


print("Chat history:", res.chat_history)
print("Summary:", res.summary)
print("Cost info:", res.cost)
