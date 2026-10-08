# Command Injection evaluation case 8
subprocess.Popen("grep " + term + " data.txt", shell=True)

