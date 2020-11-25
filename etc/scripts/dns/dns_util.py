import subprocess


class as_file:
    def __init__(self, file_or_path, mode): 
        self.file_or_path = file_or_path
        self.arg_was_file = not isinstance(file_or_path, str)
        if self.arg_was_file:
            self.file = self.file_or_path
        self.mode = mode

    def __enter__(self):
        if not self.arg_was_file:
            self.file = open(self.file_or_path, self.mode)
        return self.file

    def __exit__(self, type, value, traceback):
        if not self.arg_was_file:
            # If the arg was a file it's not our responsibility
            self.file.close()
        if value is not None:
            raise value


def reload_name_server():
    res = subprocess.run(["rndc", "reload"], capture_output=True)
    if res.returncode != 0:
        raise Exception("Error running \"rndc reload\"; exited with non-zero error code. Try running it manually?")
