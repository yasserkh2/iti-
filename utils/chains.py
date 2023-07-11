"""
This module provides two functions to generate ConversationChain and LLMChain objects for a conversation with a client and generating an SRS document respectively.

Functions:
- get_conversation_chain(chat_model): Returns a ConversationChain object for a conversation with a client to gather app details.
- get_srs_chain(instruct_model): Returns an LLMChain object for generating an SRS document based on the app details.

"""
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.chains import ConversationChain, LLMChain
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from utils.objects import Introduction, OverAllDescription
from utils.templates import get_conversation_prompt, get_srs_prompt
from utils.templates import get_intro_prompt, get_ovd_prompt


class ChainBuilder:
    def __init__(self, section_name, llm, memory, prompt, condition_text, output_parser, prompt_information, 
                 use_custom_prompt =True, condition =False, parsed_text=None, verbose = False):
        self.section_name = section_name
        self.llm = llm
        self.memory = memory
        self.prompt = prompt
        self.use_custom_prompt = use_custom_prompt
        self.condition_text = condition_text
        self.output_parser = output_parser
        self.prompt_information = prompt_information
        self.condition = condition
        self.verbose = verbose
        self.parsed_text = parsed_text
        self.chain = self.build_chain()

    def build_chain(self):
        return ConversationChain(
            llm=self.llm,
            memory=self.memory,
            prompt=self.prompt,
            verbose=self.verbose,
        )

    def __call__(self):
        yield self.build()
        yield self.format_custom_prompt()

    def __repr__(self):
        return f"""ChainBuilder(llm={self.llm}, memory={self.memory},
         prompt={self.prompt}, use_custom_prompt={self.use_custom_prompt},
          condition_text={self.condition_text}, output_parser={self.output_parser},
           verbose={self.verbose})"""


    def __str__(self):
        return self.__repr__()

    # check if the output contains the condition text or not if true return true
    def check_condition(self, output):
        self.condition = self.condition_text in output
        return self.condition
    # if condition is true then parse the output
    def parse_output(self, output):
          introduction_query = output
          parser = PydanticOutputParser(pydantic_object=self.output_parser.pydantic_object)
          prompt = PromptTemplate(
          template="get the {query} and extract {information} and generate more tokens",
          input_variables=["query"],
          partial_variables={"information": parser.get_format_instructions()},
          )

          _input = prompt.format_prompt(query=introduction_query)

          output = self.llm(_input.to_string())

          parsed_text = parser.parse(output)

          return parsed_text


    # predict the output
    def predict(self, input_text):
        output = self.chain.predict(input= input_text)
        #print("Answer From Model :",output)
        return output


   # if custom prompt is not none then format the custom prompt with the information
    def format_custom_prompt(self, information):
        if self.use_custom_prompt is True:
          if self.prompt_information != None:
            for key in self.prompt_information.dict().keys():
                self.prompt.template = self.prompt.template .replace(f'<{key}>',self.prompt_information.dict()[key])
            return self.prompt
          else:
            for parsed_text in information:
              for key in parsed_text.dict().keys():
                  self.prompt.template = self.prompt.template.replace(f'<{key}>',parsed_text.dict()[key])
            
            return self.prompt
        
        else:
            return None

        # run the chain
    def chain_run(self, input_text):
        # check if the condition is true or not
        output = self.predict(input_text)
        if self.check_condition(output):
            # parse the output
            self.parsed_text = self.parse_output(output)
            # return the output
        return output

def get_introduction_chain(chat_model):
    introduction_chain = ChainBuilder(
    	section_name='introduction',
      	llm=chat_model,
      	memory=ConversationBufferWindowMemory(),
      	prompt=get_intro_prompt(),
      	use_custom_prompt=False,
      	condition_text="""## 1. Introduction""",
      	output_parser=PydanticOutputParser(pydantic_object=Introduction),
      	prompt_information=None,
      	verbose=True,)
      
    return introduction_chain

def get_overall_description_chain(chat_model):
  overall_description_chain = ChainBuilder(
      section_name='overall description',
      llm=chat_model,
      memory=ConversationBufferWindowMemory(),
      prompt=get_ovd_prompt(),
      use_custom_prompt=True,
      condition_text="## 2. Overall Description",
      output_parser=PydanticOutputParser(pydantic_object=OverAllDescription),
      prompt_information=None,
      verbose=False,)
  
  return overall_description_chain

######################################################################################################################################
def get_conversation_chain(chat_model):
    """
    Returns a ConversationChain object for a conversation with a client to gather app details.

    Args:
    chat_model (str): The language model to use for generating responses.

    Returns:
    ConversationChain: A ConversationChain object representing the conversation chain.
    """
    conversation_prompt = get_conversation_prompt()
    conversation_chain = ConversationChain(
        llm=chat_model,
        verbose=True,
        memory=ConversationBufferMemory(),
        prompt=conversation_prompt)
    return conversation_chain

def get_srs_chain(text_model):
    """
    Returns an LLMChain object for generating an SRS document based on the app details.

    Args:
    instruct_model (str): The language model to use for generating the SRS document.

    Returns:
    LLMChain: An LLMChain object representing the SRS chain.
    """
    srs_prompt = get_srs_prompt()
    srs_chain = LLMChain(llm=text_model, prompt=srs_prompt)
    return srs_chain

