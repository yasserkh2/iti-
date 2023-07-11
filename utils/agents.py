import utils.chains as chains	# has get_conversation_chain, get_srs_chain
import utils.api as api	# To authenticate and get models from API
from utils.templates import ROUTE_TEMPLATE

class ChainLinker :
	
    def __init__(self, platform='VertexAI'):
    	self.platform = platform
    	chat_model, text_model = api.get_chat_text_models(platform=self.platform) # chat_model unused
    	self.chains = [chains.get_introduction_chain(text_model), chains.get_overall_description_chain(text_model)]
    	#print("temp_chains:",temp_chains)
    	self.current_chain_index = 0
        

    def __repr__(self):
      return f"""ChainLinker(chains={self.chains})"""

    def __str__(self):
      return self.__repr__()

    def initialize_chain(self, chain):
      if self.current_chain_index == 1:
       	output = chain.chain_run("Ask me a questions about the description of the app.")
      
      return output

    def generate(self, input_text):
      #print("chains:", self.chains)
      current_chain = self.chains[self.current_chain_index]
      output = current_chain.chain_run(input_text)
      print("output",output)
      

      if current_chain.condition:
        print('chain.condition')
        self.current_chain_index += 1
        if self.current_chain_index == len(self.chains):            
          return "Finished"
        current_chain = self.chains[self.current_chain_index]
        print("In chain:", current_chain.section_name)
        output = self.initialize_chain(current_chain)
        print('init', output)
        return output
      	  
        
        
            
      if current_chain.use_custom_prompt:
        print('current_chain.use_custom_prompt')
        parsed_texts = [chain.parsed_text for chain in self.chains[:self.current_chain_index]]
        current_chain.format_custom_prompt(parsed_texts)
        current_chain.use_custom_prompt = False

        
      return output
    def reset_state(self):
        for chain in self.chains:
            chain.memory.clear()
DocGenAI = ChainLinker




















#####################################################################################################
class TokenizersChatbot():
  def __init__(self, platform='VertexAI'):
    self.platform = platform
    self.chat_model, self.text_model = api.get_chat_text_models(platform=self.platform)
    self.conversation_chain = chains.get_conversation_chain(chat_model=self.chat_model)
    self.srs_chain = chains.get_srs_chain(self.text_model)

  def ready_to_generate_document(self, model_output):
    # If model outputs app description, generate document using srs_chain
    response_type = self.text_model(ROUTE_TEMPLATE.format(model_output))
    #print(response_type)
    if response_type == 'description': # If model has enough information about the app, generate srs.
        return True
    elif response_type == 'question':  # If model outputs questions about the app, route back to user.
        return False
    else:
      pass  # Maybe raise error?

  def generate(self, input):
    response = self.conversation_chain.predict(input=input)
    if self.ready_to_generate_document(response):
      document = self.srs_chain.predict(app_description = response)
      output = response + '\n' + document
    else:
      output = response
    return output
