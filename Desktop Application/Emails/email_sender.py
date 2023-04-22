#Program responsible for seding emails to all the recipients

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib, ssl
import csv
import json

#Function that sends the relevant emails to all recipients listed in "Email_data/recipients.csv"
def send_email():
    CONFIG_PATH = 'Emails/Config/'
    MESSAGES_PATH = 'Emails/Messages/'
    print("Sending email")
    port = 587  # For starttls

    #Obtain data about the user from config json file
    userdata = json.loads(open(CONFIG_PATH + 'userconfig.json').read())

    sender_email = userdata['user']
    search = userdata['server']
    password = userdata['password'] #This!Is!A!Password!123

    #Find the desired smtp server address
    emailbindings = json.loads(open(CONFIG_PATH + 'Emailbindings.json').read())
    smtp_server = emailbindings[search]
    print("SMTP: ", smtp_server)

    #Set up email connection
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)

        #Iterate through csv file of recipients - send emails one by one
        with open(CONFIG_PATH + 'Recipients.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                #We want to skip the header in the csv file (which will be line 0)
                if line_count > 0:
                    receiver_name = row[0]
                    receiver_email = row[1]
                    receiver_subject = row[2]

                    #Create email with headers
                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = receiver_email
                    msg['Subject'] = receiver_subject

                    #obtain the file with the desired body to send
                    filename = MESSAGES_PATH + receiver_name + "_email.txt"

                    #Read from this file, throwing exception if, for example, we cannot find the file.
                    try:
                        f = open(filename, "r")
                        body = f.read()
                        f.close()

                        #Add body to the email
                        msg.attach(MIMEText(body, 'plain'))

                        #Convert message to plain text and send
                        text = msg.as_string()
                        msg = server.sendmail(sender_email, receiver_email, text)
                        #Should just print out '{}'
                        print(msg)
                        
                    except Exception as e:
                        print("Exception sending email to " + receiver_name + ": " + str(e))

                #increment the line count
                line_count += 1
