import google.auth
import vertexai
from langchain.llms import VertexAI
from langchain.chat_models import ChatVertexAI



#LOCATION = 
def get_chat_text_models(platform):
  if platform == 'VertexAI':
    credentials, project_id = google.auth.default() # Save credentials json file in 'GOOGLE_APPLICATION_CREDENTIALS' env variable
    vertexai.init(project=project_id, credentials=credentials)
    chat_model = ChatVertexAI(model_name='chat-bison', max_output_tokens=128)
    text_model = VertexAI(model_name='text-bison', max_output_tokens=1024)
    print("text_model", text_model)
    return chat_model, text_model

    
