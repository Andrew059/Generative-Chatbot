import numpy as np
import re
from test_model import encoder_model, decoder_model, num_decoder_tokens, num_encoder_tokens, input_features_dict, target_features_dict, reverse_target_features_dict, max_decoder_seq_length, max_encoder_seq_length
#to increase performance, do this: increase the quantity of chat data used (or changing the source entirely), increase the size and capacity of the model, and allow for more training time.
#to make the conversation flow well, do this: train the model to hang onto some previous number of dialog turn, keep track of the decoder’s hidden state across dialog turn, personalize models by including user context during training or adding user context as it is included in the user input
class ChatBot:
    def __init__(self, record_data=False):
        self.record_data = record_data
        if (self.record_data):
            self.recorded_data = []

    negative_commands = ["no", "not", "nah", "stop", "nope", "naw", "sorry"]
    exit_commands = ["quit", "pause", "exit", "goodbye", "bye", "later", "stop"]

    def start_chat(self):
        user_input = input("Hello there! I am a generative chatbot that was trained using the Ghostbusters' movie script, would you like to chat with me? ")

        for word in self.negative_commands:
            if word in user_input:
                print("Ok then, goodbye!")
                return

        self.chat(user_input)

    def chat(self, user_reply):
        while not self.make_exit(user_reply):
            chatbot_response = self.generate_response(user_reply)
            user_reply = input(chatbot_response)

            if self.record_data:
                self.recorded_data.append(chatbot_response + "\t" + user_reply)

    def make_exit(self, user_input):
        for word in self.exit_commands:
            if word in user_input:
                if self.record_data:
                    self.record_convo()
                print("Ok then, goodbye!")
                return True
        return False

    def string_to_matrix(self, user_input):
        tokens = re.findall(r"[\w']+|[^\s\w]", user_input)
        user_input_matrix = np.zeros((1, max_encoder_seq_length, num_encoder_tokens), dtype="float32")

        for timestep, token in enumerate(tokens):
            if token in input_features_dict:
                user_input_matrix[0, timestep, input_features_dict[token]] = 1.
        return user_input_matrix

    def generate_response(self, user_input):
        input_matrix = self.string_to_matrix(user_input)
        states_value = encoder_model.predict(input_matrix)

        target_seq = np.zeros((1, 1, num_decoder_tokens))
        target_seq[0, 0, target_features_dict['<START>']] = 1.

        decoded_sentence = ''

        stop_condition = False
        while not stop_condition:
            output_tokens, hidden_state, cell_state = decoder_model.predict(
                [target_seq] + states_value)

            sampled_token_index = np.argmax(output_tokens[0, -1, :])
            sampled_token = reverse_target_features_dict[sampled_token_index]
            decoded_sentence += " " + sampled_token

            if (sampled_token == '<END>' or len(decoded_sentence) > max_decoder_seq_length):
                stop_condition = True

            target_seq = np.zeros((1, 1, num_decoder_tokens))
            target_seq[0, 0, sampled_token_index] = 1.


            states_value = [hidden_state, cell_state]

        chatbot_response = decoded_sentence.replace("<START>", "").replace("<END>", "")

        return chatbot_response

    def record_convo(self):
        text_file = open("recorded_convo.txt", "a")
        for line in self.recorded_data:
            text_file.write(line + "\n")
        text_file.close()

my_chatbot = ChatBot() # see if my_chatbot = ChatBot(False)
my_chatbot.start_chat()
