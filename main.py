import subprocess
import time

def server_start():
    subprocess.run(["python", "TCP_Server.py"])

def client_start():
    subprocess.run(["python", "TCP_Client.py"])

if __name__ == "__main__":
    s_process = subprocess.Popen(["python", "TCP_Server.py"])

    time.sleep(2) #Time buffer

    c_process = subprocess.Popen(["python", "TCP_Client.py"])

    try:
        c_process.wait()
    except KeyboardInterrupt:
        print("Ctrl+C was pressed - Client process ending")
        c_process.terminate()

    s_process.terminate()