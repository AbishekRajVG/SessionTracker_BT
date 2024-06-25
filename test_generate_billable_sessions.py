import tempfile
import pytest
from datetime import datetime
from io import StringIO
import os
import logging

from generate_billable_sessions import (Customer, 
                                        check_valid_log_format, 
                                        get_epoch_timestamp, 
                                        read_session_log, 
                                        generate_reports_from_logs,
                                        record_customer_session)


# Fixtures
@pytest.fixture
def customer():
    return Customer("Abishek", 1719182700)


# Customer Class Tests
def test_customer_initialization(customer):
    assert customer.name == "Abishek"
    assert customer.total_session_count == 0
    assert customer.total_session_secs == 0
    assert customer.session_stack == [1719182700]

def test_start_session(customer):
    customer.start_session(1719182900)
    assert customer.session_stack == [1719182700, 1719182900]

    customer.start_session(1719183000)
    assert customer.session_stack == [1719182700, 1719182900, 1719183000]

def test_end_session(customer):
    customer.end_session(1719184900)
    assert customer.total_session_count == 1
    assert customer.total_session_secs == 2200
    assert customer.session_stack == []

def test_multiple_start_and_end_sessions(customer):
    customer.start_session(1719182900)
    assert customer.session_stack == [1719182700, 1719182900]

    customer.start_session(1719183000)
    assert customer.session_stack == [1719182700, 1719182900, 1719183000]

    customer.end_session(1719183500)
    assert customer.total_session_count == 1
    assert customer.total_session_secs == 500
    assert customer.session_stack == [1719182700, 1719182900]

    customer.end_session(1719183000)
    assert customer.total_session_count == 2
    assert customer.total_session_secs == 600
    assert customer.session_stack == [1719182700]


# Utility Functions Tests
def test_check_valid_log_format():
    valid_log = "12:00:00 Abishek Start"
    invalid_log = "[2010-04-24 07:52:07,300] DEBUG - [main] Execution complete."
    assert check_valid_log_format(valid_log)
    assert not check_valid_log_format(invalid_log)


def test_get_epoch_timestamp():
    ts = get_epoch_timestamp("12:00:00")
    expected_ts = int(datetime.now().replace(hour=12, minute=0, second=0, microsecond=0).timestamp())
    assert ts == expected_ts


def test_read_session_log():
    log = "12:00:00 Abishek Start"
    epoch_timestamp, customer_name, session_boundary = read_session_log(log)
    expected_ts = int(datetime.now().replace(hour=12, minute=0, second=0, microsecond=0).timestamp())
    assert epoch_timestamp == expected_ts
    assert customer_name == "Abishek"
    assert session_boundary == "Start"


@pytest.fixture(autouse=True)
def reset_customer_class():
    Customer.customer_dict = {}
    Customer.active_customer_list = []
    Customer.earliest_log_timestamp = 0


def test_record_customer_session_new_customer_normal_start():
    record_customer_session("Raj", 1719309600, "Start")
    assert "Raj" in Customer.customer_dict
    customer = Customer.customer_dict["Raj"]
    assert customer.total_session_count == 0
    assert customer.total_session_secs == 0
    assert len(customer.session_stack) == 1


def test_record_customer_session_new_customer_direct_end():
    record_customer_session("Raj", 1719309600, "End")
    assert "Raj" in Customer.customer_dict
    customer = Customer.customer_dict["Raj"]
    assert customer.total_session_count == 1
    assert customer.total_session_secs == 0
    assert len(customer.session_stack) == 0


def test_record_customer_session_known_customer_normal_start():
    record_customer_session("Raj", 1719309600, "Start")
    record_customer_session("Raj", 1719309700, "End")

    # make sure customer is known
    assert "Raj" in Customer.customer_dict
    customer = Customer.customer_dict["Raj"]

    # make sure no sessions
    assert len(customer.session_stack) == 0

    # add new session same customer name
    record_customer_session("Raj", 1719309900, "Start")

    assert "Raj" in Customer.customer_dict
    customer = Customer.customer_dict["Raj"]
    assert customer.total_session_count == 1
    assert customer.total_session_secs == 100
    assert len(customer.session_stack) == 1


def test_record_customer_session_known_customer_direct_end():
    record_customer_session("Raj", 1719309600, "Start")
    record_customer_session("Raj", 1719309700, "End")

    # make sure customer is known
    assert "Raj" in Customer.customer_dict
    customer = Customer.customer_dict["Raj"]

    # make sure no sessions
    assert len(customer.session_stack) == 0

    # add new session same customer name
    record_customer_session("Raj", 1719309900, "End")

    assert "Raj" in Customer.customer_dict
    customer = Customer.customer_dict["Raj"]
    assert customer.total_session_count == 2
    assert customer.total_session_secs == 400
    assert len(customer.session_stack) == 0


@pytest.fixture(autouse=True)
def reset_customer_class():
    Customer.customer_dict = {}
    Customer.active_customer_list = []
    Customer.earliest_log_timestamp = 0


def test_generate_reports_from_logs():
    log_content = '\n'.join(("",
        "14:02:03 ALICE99 Start",
        "14:02:05 CHARLIE End",
        "14:02:34 ALICE99 End",
        "14:02:58 ALICE99 Start",
        "14:03:02 CHARLIE Start",
        "14:03:33 ALICE99 Start",
        "14:03:35 ALICE99 End",
        "14:03:37 CHARLIE End",
        "14:04:05 ALICE99 End",
        "14:04:23 ALICE99 End",
        "14:04:41 CHARLIE Start"
    ))

    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        tmpfile.write(log_content.encode('utf-8'))
        tmpfile_path = tmpfile.name
    
    generate_reports_from_logs(tmpfile_path)
    os.remove(tmpfile_path)

    assert "ALICE99" in Customer.customer_dict
    assert "CHARLIE" in Customer.customer_dict

    cust1 = Customer.customer_dict["ALICE99"]
    cust2 = Customer.customer_dict["CHARLIE"]

    assert cust1.total_session_count == 4
    assert cust1.total_session_secs == 240
    assert len(cust1.session_stack) == 0


    assert cust2.total_session_count == 3
    assert cust2.total_session_secs == 37
    assert len(cust2.session_stack) == 0


def test_generate_reports_from_logs_file_not_found(caplog):
    with pytest.raises(FileNotFoundError) as excinfo:  
            generate_reports_from_logs("non_existent_file.txt")  
    assert str(excinfo.value) == "Unfortunately, File non_existent_file.txt not found"  


if __name__ == '__main__':
    pytest.main()
