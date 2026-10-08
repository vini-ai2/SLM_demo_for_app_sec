# Command Injection evaluation case 5
subprocess.run(["sh", "-c", "echo " + message])

