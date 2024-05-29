import boto3
import json
from io import BytesIO
from datetime import datetime
import os

#agentId = "CYKESWD1CO" #INPUT YOUR AGENT ID HERE
#agentAliasId = "2VQNHMXR4L" # Hits draft alias, set to a specific alias id for a deployed version
theRegion = "us-west-2"
agentId =  os.environ['AgentId']
agentAliasId = os.environ['AgentAliasId']

os.environ["AWS_REGION"] = theRegion
region = os.environ.get("AWS_REGION")
llm_response = ""

def lambda_handler(event, context):
    
    sessionId = event["sessionId"]
    question = event["question"]
    endSession:bool = False
    enable_trace:bool = True
    
    print(f"Session: {sessionId} asked question: {question}")

    try: 
        # create the client to connect to bedrock agent
        bedrock_agent_runtime_client = boto3.client('bedrock-agent-runtime')

        # invoke the agent API
        agentResponse = bedrock_agent_runtime_client.invoke_agent(
            inputText=question,
            agentId=agentId,
            agentAliasId=agentAliasId, 
            sessionId=sessionId,
            enableTrace=enable_trace, 
            endSession=endSession
        )
        
        response, trace_data = decode_response(agentResponse)

        return {
            "status_code": 200,
            "body": json.dumps({"response": response, "trace_data": trace_data})
        }
    except Exception as e:
        return {
            "status_code": 500,
            "body": json.dumps({"error": str(e)})
        }


def decode_response(agentResponse):

    print("Decoding response")

    agent_answer = ""
    trace_info = "["

    event_stream = agentResponse['completion']

    for event in event_stream:        
        if 'chunk' in event:
            data = event['chunk']['bytes']
            print(f"Final answer ->\n{data.decode('utf8')}")
            agent_answer = data.decode('utf8')
            end_event_received = True
            # End event indicates that the request finished successfully
        elif 'trace' in event:
            trace_info += json.dumps(event['trace'], indent=2) + ","
            #print(json.dumps(event['trace'], indent=2))
        else:
            print("Error decoding response: ", str(event))
            raise Exception("unexpected event.", event)
        
    # Return both the captured output and the final response
    trace_info_formatted = trace_info[:-1] if trace_info[-1]==',' else trace_info
    trace_info_formatted += "]"
    return trace_info_formatted, agent_answer
    

