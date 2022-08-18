import email
import re


class GetEmailDetails:
    def __init__(self, email_body):
        self.email = email_body
        self.name_regex = re.compile("full name:\s(\w+\s\w+)", re.IGNORECASE)
        self.email_regex = re.compile(
            "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"
        )
        self.phone_number = re.compile("(254|0)(\d{9})")  # 263
        self.issue_section = re.compile(
            "Section:\s([a-zA-Z]+\s?)([a-zA-Z]+\s?)?([a-zA-Z]+\s?)?", re.IGNORECASE)
        self.issue_description = re.compile(
            "Issue:", re.IGNORECASE)

    def get_details(self):
        self.get_name()
        self.get_email()
        self.get_phone_number()
        self.get_issue_section()
        self.get_issue_description()

    def get_name(self):
        try:
            fullname = self.name_regex.search(self.email).group(1)
            print("Full name: ", fullname)
            if fullname:
                return fullname
            return None
        except Exception as e:
            print("fullname error:{}".format(e))

    def get_email(self):
        try:
            email_address = self.email_regex.findall(
                self.email).strip('helpdesk@gokhanmasterspacejv.co.ke')
            print("Email address: ", email_address)
            if email_address:
                return email_address[0]
            return None
        except Exception as e:
            print("get email error:{}".format(e))

    def get_phone_number(self):
        try:
            phone_number = self.phone_number.findall(self.email)
            print("Phone number: ", phone_number)
            if phone_number:
                return str(phone_number[0][1])
            return None
        except Exception as e:
            print("get tel error:{}".format(e))

    def get_issue_section(self):
        try:
            section = ''
            words = ['Hardware', 'Software', 'Applications',
                     'Infrastructure and Networking', 'Database', 'Human Resource', 'Technical', 'General']
            for word in words:
                if word.lower() in self.email.lower():
                    section = word
                    break
            if section:
                return section
            return None
        except Exception as e:
            print("get section error:{}".format(e))

    def get_issue_description(self):
        try:
            description = self.issue_description.search(self.email).end()
            issue_description = self.email[description:]
            print("Description: ", issue_description)

            if issue_description:
                return issue_description
            return None
        except Exception as e:
            print("get description error:{}".format(e))

    def process_section(self, section):
        try:
            counter = 0
            for sec in section:
                if sec.endswith("\n"):
                    break

                counter += 1

            if counter == 0:
                return re.sub("\n", "", section[0])

            else:
                return " ".join(section[:counter+1])
        except Exception as e:
            print("process section error:{}".format(e))
