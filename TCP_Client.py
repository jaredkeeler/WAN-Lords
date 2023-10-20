import queue
import socket
import random
import string
import time
import logging
import threading

def randomPassenger(): #Generates a random passenger
    name_length = random.randint(5, 15)
    passenger_name = ''.join(random.choice(string.ascii_letters) for _ in range(name_length))
    return passenger_name

airport_IATAcodes = ["ANC", "SEA", "BRW", "OTZ", "FAI"]
delay = 2

def log4client(logQ): #Sets up the client log
    format_lg = '%(asctime)s - %(levelname)s - %(msg)s'
    logging.basicConfig(level=logging.INFO, format=format_lg)

    handlef = logging.FileHandler(f"TCP_log4client.txt")
    handlef.setFormatter(logging.Formatter(format_lg))

    logger = logging.getLogger()
    logger.addHandler(handlef)

    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            logger.removeHandler(handler)

    while True:
        lg_rcd = logQ.get()
        if lg_rcd is None:
            break
        logging.info(lg_rcd)

def clientLogic(initial_airport, server_address, logQ, do3flights): #The logic for the client flights
    try:
        while True:
            middle_airport = random.choice(airport_IATAcodes)

            if do3flights:
                while middle_airport == initial_airport or middle_airport == "FAI" or middle_airport == "OTZ" or middle_airport == "BRW":
                    middle_airport = random.choice(airport_IATAcodes)
                airport_final = random.choice(airport_IATAcodes)
                while airport_final == middle_airport:
                    airport_final = random.choice(airport_IATAcodes)

            else:
                while middle_airport == initial_airport:
                    middle_airport = random.choice(airport_IATAcodes)
                airport_final = ""

            passenger_details = randomPassenger()

            if initial_airport not in airport_IATAcodes:
                logQ.put("Invalid IATA code for origin airport.")
                continue
            if middle_airport not in airport_IATAcodes:
                logQ.put("Invalid IATA code for destination airport.")
                continue
            if airport_final and airport_final not in airport_IATAcodes:
                logQ.put("Invalid IATA code for layover airport.")
                continue

            if do3flights:
                msg = f"{initial_airport},{middle_airport},{airport_final},{passenger_details}"
            else:
                msg = f"{initial_airport},{middle_airport},{passenger_details}"

            if msg == '.':
                break

            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(server_address)

            client_socket.sendall(msg.encode())
            logQ.put(f"Sent to the server: {msg}")

            data = client_socket.recv(1024)
            logQ.put(f"Received from the server: {data.decode()}")

            client_socket.close()

            time.sleep(delay)

    except KeyboardInterrupt:
        logQ.put("Client process ended by user.")
    except Exception as e:
        logQ.put(f"Err: {str(e)}")
    finally:
        logQ.put(None)

if __name__ == "__main__":
    server_address = ('127.0.0.1', 12349)
    num_clients = 200

    logQ = queue.Queue()
    logT = threading.Thread(target=log4client, args=(logQ,))
    logT.start()

    threads = []
    for i in range(num_clients):
        IATAcode = random.choice(airport_IATAcodes)
        do3flights = random.choice([True, False])
        thread = threading.Thread(target=clientLogic, args=(IATAcode, server_address, logQ, do3flights))
        thread.start()
        threads.append(thread)

    try:
        for thread in threads:
            thread.join()

    except KeyboardInterrupt:
        print("Ctrl+C was pressed - All threads ending")
        for thread in threads:
            thread.join()

    logQ.put(None)
    logT.join()