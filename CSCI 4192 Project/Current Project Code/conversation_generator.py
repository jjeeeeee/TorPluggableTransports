import random as r
import json
import string


# Parameters for conversation generation
N1 = 1          # Min characters for message
N2 = 100        # Max characters for message
N3 = 1          # Min gap between messages/delay in responses (in seconds)
N4 = 20         # Max gap between messages/delay in responses (in seconds)
N5 = 180        # Min conversation session length (in seconds)
N6 = 300        # Max conversation session length (in seconds)
N7 = 30         # Min gap between conversation sessions (in seconds)
N8 = 60         # Max gap between conversation sessions (in seconds)
N9 = 1          # Min number of messages in a message burst
N10 = 5         # Max number of messages in a message burst
MAX_CONVERSATION_LENGTH = 60 * 60 * 4    # Default to 4-hour conversation
FIRST_AUTHOR_NAME = "User 1"
SECOND_AUTHOR_NAME = "User 2"
CHARS = string.ascii_letters + string.digits


def generate_conversation():
  first_message = True
  stop_generating = False
  author_flag = True
  conversation_remaining = MAX_CONVERSATION_LENGTH

  with open("parsed_conversation.txt", "w") as output_file:
    while True:
      conversation_session_length = r.randint(N5, N6)
      conversation_session_break = r.randint(N7, N8)
      session_over = False

      while True:
        message_burst_count = r.randint(N9, N10)

        for i in range(message_burst_count):
          content_length = r.randint(N1, N2)
          content = ''.join(r.choices(CHARS, k=content_length))
          delay = 0
          if not first_message:
            delay = r.randint(N3, N4)
          else:
            first_message = False

          message = {
            'Author': FIRST_AUTHOR_NAME if author_flag else SECOND_AUTHOR_NAME,
            'Delay': delay,
            'Content': content
          }
          json.dump(message, output_file, ensure_ascii=False)
          output_file.write("\n")

          conversation_remaining -= delay
          if conversation_remaining <= 0:
            session_over = True
            stop_generating = True
            break
          conversation_session_length -= delay
          if conversation_session_length <= 0:
            session_over = True
            break

        author_flag = not author_flag
        if session_over:
          break

      if stop_generating:
        break

      message = {
        'Author': "BreakMessage",
        'Delay': conversation_session_break,
        'Content': None
      }
      json.dump(message, output_file, ensure_ascii=False)
      output_file.write("\n")

      conversation_remaining -= conversation_session_break
      if conversation_remaining <= 0:
        break


if __name__ == '__main__':
  generate_conversation()
