from http.server import BaseHTTPRequestHandler, HTTPServer


class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            self.completed_items = file.readlines()
            file.close()
        except Exception:
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def add(self, args):
        self.read_current()
        priority = int(args[0])
        to_print = args[-1]
        task = ""
        temp = ""
        if to_print == False: task = " ".join(args[1:-1])
        else: task = " ".join(args[1:])
        if priority in self.current_items.keys():
            temp = self.current_items[priority]
            self.current_items[priority] = task
            self.write_current()
            self.add([priority + 1, temp, False])
        else:
            self.current_items[priority] = task
            self.write_current()
        if to_print != False:
            print(f"Added task: \"{task}\" with priority {priority}")

    def done(self, args):
        self.read_current()
        try:
            self.completed_items.append(self.current_items[int(args[0])])
            del self.current_items[int(args[0])]
            self.write_completed()
            self.write_current()
            print(f"Marked item as done.")
        except Exception:
            print(f"Error: no incomplete item with priority {args[0]} exists.")

    def delete(self, args):
        self.read_current()
        try:
            del self.current_items[int(args[0])]
            print(f"Deleted item with priority {args[0]}")
            self.write_current()
        except Exception:
            print(f"Error: item with priority {args[0]} does not exist. Nothing deleted.")

    def ls(self):
        self.read_current()
        index = 1
        for key in sorted(self.current_items.keys()):
            print(f"{index}. {self.current_items[key]} [{key}]")
            index += 1

    def report(self):
        self.read_completed()
        self.read_current()

        print(f"Pending : {len(self.current_items)}")
        self.ls()
        print(f"\nCompleted : {len(self.completed_items)}")
        for i in range(1, len(self.completed_items) + 1):
            if i == len(self.completed_items):
                print(f"{i}. {self.completed_items[i-1]}", end = "")
            else:
                print(f"{i}. {self.completed_items[i-1]}")

    def render_pending_tasks(self):
        # Complete this method to return all incomplete tasks 
        self.read_current()
        content = "<ol>"
        for key in sorted(self.current_items.keys()):
            content += f"<li>{self.current_items[key]} [{key}]</li>\n"

        return f"<h1> Show Incomplete Tasks Here </h1>\n{content}\n</ol>"

    def render_completed_tasks(self):
        # Complete this method to return all completed tasks as HTML
        self.read_completed()
        content = "<ol>"
        for item in self.completed_items:
            content += f"<li>{item}</li>"

        return f"<h1>Completed Tasks:</h1>\n{content}\n</ol>"


class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()
        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())