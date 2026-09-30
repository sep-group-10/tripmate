from langchain_core.tools import BaseTool

from app.services.tools.candidate_retriever import candidate_retriever
from app.services.tools.constraint_validator import constraint_validator
from app.services.tools.cost_estimator import cost_estimator
from app.services.tools.route_optimizer import route_optimizer
from app.services.tools.scheduling_engine import scheduling_engine
from app.services.tools.scoring_engine import scoring_engine
from app.services.tools.weather_validator import weather_validator

TOOLS: dict[str, BaseTool] = {
    "candidate_retriever": candidate_retriever,
    "scoring_engine": scoring_engine,
    "scheduling_engine": scheduling_engine,
    "route_optimizer": route_optimizer,
    "weather_validator": weather_validator,
    "cost_estimator": cost_estimator,
    "constraint_validator": constraint_validator,
}
