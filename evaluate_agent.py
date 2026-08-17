import logfire
from langsmith import Client, evaluate
from langsmith.evaluation import LangChainStringEvaluator
from agent.netops_agent import create_agent

logfire.configure(pydantic_plugin=logfire.PydanticPlugin(record="all"))
logfire.instrument_langchain()
client = Client()
agent_executor = create_agent()

def predict_diagnostics(inputs: dict) -> dict:
    with logfire.span("evaluate_agent_prediction", query=inputs["question"]):
        return {"output": agent_executor.invoke({"input": inputs["question"]})["output"]}

dataset_name = "NetOps_RAG_Diagnostics"
if not client.has_dataset(dataset_name=dataset_name):
    dataset = client.create_dataset(dataset_name=dataset_name, description="Testing ISP diagnostic accuracy.")
    examples = [
        ({"question": "Client 'ian_home' says their internet is down. Check PPPoE."}, {"reference": "User is disconnected."}),
        ({"question": "What is the default MTU for RouterOS PPPoE?"}, {"reference": "The default MTU is 1480."})
    ]
    for i, o in examples:
        client.create_example(inputs=i, outputs=o, dataset_id=dataset.id)

if __name__ == "__main__":
    evaluate(
        predict_diagnostics,
        data=dataset_name,
        evaluators=[LangChainStringEvaluator("qa")],
        experiment_prefix="netops-agent-eval",
        metadata={"version": "1.0"}
    )
