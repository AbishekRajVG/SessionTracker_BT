import sys
from datetime import datetime, timezone
import re

class Customer:
    """The Customer class defines and tracks customer sessions per customer"""
    customer_dict = {}
    active_customer_list = []
    earliest_log_timestamp = 0


    def __init__(self, name: str, start_ts: int) -> None:
        """Initialize a new Customer instance.

        Args:
            name (str): The name of the customer.
            start_ts (int): The start timestamp of the session in epoch time.
        """
        self.name: str = name
        self.total_session_count: int = 0
        self.total_session_secs: int = 0
        self.session_stack: list = [start_ts]

        # every initialized customer object is saved in customer list
        Customer.customer_dict[self.name] = self
        # every active customer is also tracked to catch end session anamoly
        Customer.active_customer_list.append(self)
    

    def start_session(self, start_ts:int) -> None:
        """Start a new session for the customer.

        Args:
            start_ts (int): The start timestamp of the session in epoch time.
        """
        self.session_stack.append(start_ts)
        if self not in Customer.active_customer_list: 
            Customer.active_customer_list.append(self)


    def end_session(self, end_ts: int) -> None:
        """End a session for the customer.

        Args:
            end_ts (int): The end timestamp of the session in epoch time.
        """
        # add to session count
        self.total_session_count += 1

        # get the latest start_ts to pair with the end_ts
        start_ts = self.session_stack.pop()
        self.total_session_secs += (end_ts - start_ts)
 
        # if all sessions have ended, the customer is no longer active
        if len(self.session_stack) == 0:
            Customer.active_customer_list.remove(self)
    

    def __str__(self) -> str:
        """Printable string represntation of customer objects.
        
        Returns:
            str: String of customer attributes.
        """
        return str(self.name) + " " \
            + str(self.total_session_count) + " " \
                + str(self.total_session_secs)



def check_valid_log_format(log: str) -> bool:
    """Verify if the log is in a valid format.

    Returns:
        bool: True if the log format is valid, otherwise False. 
    
    """
    valid_log_pattern = re.compile(r'^\d{2}:\d{2}:\d{2}\s+\w+\s+(Start|End)$')
    return valid_log_pattern.match(log)


def get_epoch_timestamp(hhmmss: str) -> int:
    """Convert a time string (HH:MM:SS) to an epoch timestamp.

    Args:
        hhmmss (str): The time string in HH:MM:SS format.
    Returns: 
        int: The corresponding epoch timestamp.
    """
    ts = datetime.strptime(hhmmss, "%H:%M:%S")
    today = datetime.now()
    return int(ts.replace(year=today.year, month=today.month, day=today.day).timestamp())


def read_session_log(log) -> tuple:
    """Extract the timestamp, customer name, and session boundary from a log entry.

    Args:
        log (str): The log entry as a string.
    Returns: 
        tuple: A tuple containing the epoch timestamp, customer name, and session boundary.
    """
    # get epoch timestamp col 1 - move to a method to clean up
    epoch_timestamp = get_epoch_timestamp(log.split()[0])
    # get customer name col 2
    customer_name = log.split()[1]
    # get col 3 get sesssion Start / End
    session_boundary = log.split()[2]

    return epoch_timestamp, customer_name, session_boundary


def record_customer_session(
    customer_name: str, 
    epoch_timestamp: int, 
    session_boundary: str
) -> None:
    """Record a customer's session based on the log entry details 
    and persists reports in customer objects.

    Args:
        customer_name (str): The name of the customer.
        epoch_timestamp (int): The timestamp of the session in epoch time.
        session_boundary (str): The session boundary, either "Start" or "End".
    """            
    # record the first ever log timestamp
    if Customer.earliest_log_timestamp == 0: 
        Customer.earliest_log_timestamp = epoch_timestamp

    # case 1: New Customer
    if(customer_name not in Customer.customer_dict):
        # case 1.1: new customer normal start
        if(session_boundary == "Start"):
            customer = Customer(customer_name, epoch_timestamp)
        # case 1.2: new customer unknown start, direct end
        else:
            # Corner case when a new customer has no start session
            customer = Customer(customer_name, Customer.earliest_log_timestamp)
            customer.end_session(epoch_timestamp)

    # case 2: Known customer
    else:
        # case 2.1: Known customer normal start
        customer = Customer.customer_dict[customer_name]
        if(session_boundary == "Start"):
            customer.start_session(epoch_timestamp)
        # case 2.2: Corner case when a known customer has no matching start session
        else:
            if len(customer.session_stack) == 0:
                customer.start_session(Customer.earliest_log_timestamp)
            customer.end_session(epoch_timestamp)


def generate_reports_from_logs(file_path: str) -> None:
    """Primary driver function that generates customer session reports from a log file.

    Args:
        file_path (str): The path to the log file.
    """
    try:
        with open(file_path, 'r') as reader:
            for log in reader.readlines():
                if (check_valid_log_format(log)):
                    # read each valid log and extract timestamp, name and boundary
                    epoch_timestamp, customer_name, session_boundary = read_session_log(log)

                    # generate report per log and persist as customer objects
                    record_customer_session(customer_name, epoch_timestamp, session_boundary)

                    # update the the last valid log until exit
                    last_valid_log = log
            
            # at the eof of log file after loop ends - corner case zero valid logs 
            log_last_ts = 0 if (Customer.earliest_log_timestamp == 0) else get_epoch_timestamp(last_valid_log.split()[0])

            # handle unended sessions
            for customer in Customer.active_customer_list:
                while len(customer.session_stack) != 0:
                    customer.end_session(log_last_ts)
    except FileNotFoundError as fnfe:
        raise FileNotFoundError(f"Unfortunately, File {file_path} not found")  
        # print("File {file_path} not found")

    except Exception as e:
        raise Exception(f"An error occurred: {e}")


def print_fair_bill_session_reports() -> None:
    for customer in Customer.customer_dict.values():
        print(customer)


# main function
if __name__ == '__main__':
    try:
        generate_reports_from_logs(sys.argv[1])
    except FileNotFoundError as fnfd:
        print(fnfd)
    print_fair_bill_session_reports()

    



