import os
import sys
import json
import getopt
import smtplib
import email.message
import urllib.request
from datetime import datetime

current_abspath = os.path.abspath(os.path.dirname(__file__))
website_file_path = current_abspath + "/assets/websites.json"
up_template_path = current_abspath + "/assets/up_template.html"
down_template_path = current_abspath + "/assets/down_template.html"
log_file = current_abspath + "/assets/logs.txt"


def json_read():
    global website_file_path
    with open(website_file_path, 'r') as openfile:
        file_json = json.load(openfile)
    return file_json


def json_write(updated_json):
    global website_file_path
    new_json = json.dumps(updated_json, indent=4)
    with open(website_file_path, "w") as write_file:
        write_file.write(new_json)


def update_json(original_json, error_list=[]):
    if error_list != []:
        error_url_list = []
        for error in error_list:
            found = False
            for old_error in original_json[0]["error_list"]:
                if old_error["url"] == error["url"]:
                    error_url_list.append(
                        {"name": old_error["name"], "url": old_error["url"], "error": old_error["error"], "time": old_error["time"]})
                    found = True
            if not found:
                error_url_list.append(
                    {"name": error["name"], "url": error["url"], "error": str(error["error"]), "time": error["time"].strftime("%Y-%m-%d : %H:%M:%S")})

        original_json[0]["error_list"] = error_url_list
    else:
        original_json[0]["error_list"] = []
    return original_json


def email_send(name, email_addr, username, password, server, port, emailfrom, msg, cc_email, title):
    try:
        email_content = msg
        email_server = server + ": " + port
        msg = email.message.Message()
        msg['Subject'] = title
        msg['From'] = emailfrom
        msg['To'] = email_addr
        msg['Cc'] = ', '.join(cc_email)
        msg.add_header('Content-Type', 'text/html')
        msg.set_payload(email_content)
        smtp = smtplib.SMTP(email_server)
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(msg)
        print("email sent to: {} - {}".format(name, email_addr))
    except:
        print("Failed to send the email. Please check the email server credentials.")


def upTest(website_list, error_list, ignore_error_list):
    temp_error_list = []
    temp_success_list = []
    for website in website_list:
        website_url = website["url"]
        website_name = website["name"]
        try:
            status = urllib.request.urlopen(website_url).getcode()
        except Exception as error:
            status = error
        if status != 200:
            if not ignore_error_check(ignore_error_list, status):
                temp_error_list.append(
                    {"name": website_name, "url": website_url, "error": status, "time": datetime.now()})
        else:
            for item in error_list:
                if item["url"] == website_url:
                    temp_success_list.append({"name": website_name, "url": website_url,
                                             "error": item["error"], "time_start": item["time"], "time_end": datetime.now()})
    return temp_error_list, temp_success_list


def read_template(type):
    global up_template_path
    global down_template_path
    with open(up_template_path if type == "up" else down_template_path, "r") as file:
        content = file.read()
    return content


def msg_create(result, to_name, type):
    if type == "up":
        start_time = datetime.strptime(
            result["time_start"], "%Y-%m-%d : %H:%M:%S")
        end_time = result["time_end"]
        duration = end_time - start_time
        html_content = read_template("up")
        html_content = html_content.replace("$username", to_name)
        html_content = html_content.replace("$site_name", result["name"])
        html_content = html_content.replace("$site_url", result["url"])
        html_content = html_content.replace(
            "$error_code", str(result["error"]).replace("<", "").replace(">", ""))
        html_content = html_content.replace(
            "$error_start_time", start_time.strftime("%Y-%m-%d : %H:%M:%S"))
        html_content = html_content.replace(
            "$error_resolved_time", result["time_end"].strftime("%Y-%m-%d : %H:%M:%S"))
        html_content = html_content.replace(
            "$error_duration", str(duration).split(".")[0])
        return html_content

    elif type == "down":
        html_content = read_template("down")
        html_content = html_content.replace("$username", to_name)
        html_content = html_content.replace("$site_name", result["name"])
        html_content = html_content.replace("$site_url", result["url"])
        html_content = html_content.replace(
            "$error_code", str(result["error"]).replace("<", "").replace(">", ""))
        html_content = html_content.replace(
            "$error_start_time", result["time"].strftime("%Y-%m-%d : %H:%M:%S"))
        return html_content


def error_site_list_creator(data):
    temp_list = []
    for i in data:
        temp_list.append(i["name"])
    return temp_list


def logger(condition, name, url, time, error):
    global log_file
    text = "\n{} - {} - {} ({}) - {}".format(condition, time, name, url, error)
    write_type = "a" if os.path.isfile(log_file) else "w"
    with open(log_file, write_type) as write_file:
        write_file.write(text)


def ignore_error_check(ignore_error_list, error):
    for item in ignore_error_list:
        if str(error).find(item) != -1:
            return True
    return False


def user_arg(argv):
    arg_emailuser = ""
    arg_emailpass = ""
    arg_emailserv = ""
    arg_emailport = ""
    arg_emailfrom = ""
    arg_help = "{0} -u <emailuser> -p <emailpass> -s <emailserv> -o <emailport> -f <emailfrom>".format(
        argv[0])

    try:
        opts, args = getopt.getopt(argv[1:], "hu:p:s:o:f:", [
                                   "help", "emailuser=", "emailpass=", "emailserv=", "emailport=", "emailfrom="])
    except:
        print(arg_help)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)
            sys.exit(2)
        elif opt in ("-u", "--emailuser"):
            arg_emailuser = arg
        elif opt in ("-p", "--emailpass"):
            arg_emailpass = arg
        elif opt in ("-s", "--emailserv"):
            arg_emailserv = arg
        elif opt in ("-o", "--emailport"):
            arg_emailport = arg
        elif opt in ("-f", "--emailfrom"):
            arg_emailfrom = arg

    return arg_emailuser, arg_emailpass, arg_emailserv, arg_emailport, arg_emailfrom


def main():
    if __name__ == "__main__":
        emailuser, emailpass, emailserv, emailport, emailfrom = user_arg(
            sys.argv)

    json_file = json_read()
    website_list = json_file[0]["website"]
    web_error_list = json_file[0]["error_list"]
    ignore_error_list = json_file[0]["ignore_error_list"]
    to_name = json_file[1]["to_email_info"]["name"]
    to_email = json_file[1]["to_email_info"]["email"]
    cc_email = json_file[1]["cc_email_list"]

    web_error_site_name_list = error_site_list_creator(web_error_list)
    error_list, success_list = upTest(
        website_list, web_error_list, ignore_error_list)

    if error_list != []:
        for error in error_list:
            if error["name"] not in web_error_site_name_list:
                msg = msg_create(error, to_name, "down")
                title = "Monitor is DOWN: {}".format(error["name"])
                email_send(to_name, to_email, emailuser, emailpass,
                           emailserv, emailport, emailfrom, msg, cc_email, title)
            logger("DOWN", error["name"], error["url"],
                   error["time"], error["error"])
        json_write(update_json(json_file, error_list))
    else:
        json_write(update_json(json_file))

    if success_list != []:
        for success in success_list:
            msg = msg_create(success, to_name, "up")
            title = "Monitor is UP: {}".format(success["name"])
            email_send(to_name, to_email, emailuser, emailpass,
                       emailserv, emailport, emailfrom, msg, cc_email, title)
            logger("UP", success["name"], success["url"],
                   success["time_end"], success["error"])


main()
