import traceback
import sys

class CustomException(Exception):

    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        # FIXED: Completed the broken argument list
        self.error_message = self.get_detailed_error_message(error_message, error_detail)

    # FIXED: Indented to sit inside the class
    def get_detailed_error_message(self, error_message, error_detail: sys):
        _, _, exc_tb = error_detail.exc_info()
        file_name = exc_tb.tb_frame.f_code.co_filename
        line_number = exc_tb.tb_lineno
        return f"Error in {file_name}, line {line_number} : {error_message}"

    # FIXED: Indented to sit inside the class
    def __str__(self):
        return self.error_message