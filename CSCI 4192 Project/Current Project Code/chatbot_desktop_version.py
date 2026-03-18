import pyautogui
import pyperclip
import time
import json
import html


# ================= CONFIG =================
CONVERSATION_FILE = 'parsed_conversation.txt'
MY_AUTHOR = 'User 1'
OTHER_AUTHOR = 'User 2'
BREAK_AUTHOR = 'BreakMessage'

# Desktop measurements - YOU MUST CHANGE THESE IF USING A NEW DEVICE
BUTTON_PRESS_X_COORD = 1564
BUTTON_PRESS_Y_COORD = 956
COPY_X_COORD = 762
COPY_Y_COORD = 952
WRITE_X_COORD = 762
WRITE_Y_COORD = 1030

POLL_INTERVAL = 1      # seconds between UI checks
pyautogui.FAILSAFE = True


# ================= HELPERS =================
def consume_received_messages(conversation, start_index, seen_text):
    # Advance index if seen_text matches any upcoming message
    i = start_index

    while i < len(conversation):
        msg = conversation[i]

        # Stop if it's our turn
        if msg['Author'] == MY_AUTHOR:
            break

        # Go back if it's a break
        if msg['Author'] == BREAK_AUTHOR:
            return i - 1

        if html.unescape(msg['Content']) == seen_text:
            return i + 1  # consume up to here

        i += 1

    return start_index


def load_conversation(path):
    messages = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            messages.append(json.loads(line))
    return messages


def read_latest_message():
    # Click New Messages button if it's there
    pyautogui.moveTo(BUTTON_PRESS_X_COORD, BUTTON_PRESS_Y_COORD, duration=0.2)
    pyautogui.click(clicks=1, interval=0.1)
    time.sleep(0.1)

    pyautogui.moveTo(COPY_X_COORD, COPY_Y_COORD, duration=0.2)
    pyautogui.click(clicks=3, interval=0.1)
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.1)
    return pyperclip.paste().strip()


def send_message(message):
    pyautogui.moveTo(WRITE_X_COORD, WRITE_Y_COORD, duration=0.2)
    pyautogui.click()
    time.sleep(0.1)
    pyperclip.copy(message)
    time.sleep(0.1)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.press('enter')


def wait_for_expected_message(expected_text):
  seen = read_latest_message()
  print(f"Expected: {expected_text}, Received: {seen}")
  if seen == expected_text:
    return True
  else:
    return False


def replay_conversation():
    conversation = load_conversation(CONVERSATION_FILE)

    i = 0
    while i < len(conversation):
        msg = conversation[i]
        author = msg['Author']
        delay = msg['Delay']
        if msg['Content'] is not None:
            content = html.unescape(msg['Content'])
        else:
            # Session over, take a break
            print("[BREAK] Taking a break between sessions")
            i += 1
            time.sleep(delay)

        if author == MY_AUTHOR:
            # SEND STATE
            print(f"[SEND] {content}")
            time.sleep(delay)
            send_message(content)
            i += 1

        elif author == OTHER_AUTHOR:
            # WAIT STATE
            print("[WAIT] Waiting for other side...")

            while True:
                seen = read_latest_message()

                new_i = consume_received_messages(conversation, i, seen)
                if new_i != i:
                    i = new_i
                    break

                time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    replay_conversation()
