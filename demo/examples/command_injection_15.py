# Command Injection evaluation case 15
subprocess.run(["sh", "-c", "echo " + message])

