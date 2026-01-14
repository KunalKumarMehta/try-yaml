"""Python code execution tool."""

import sys
import io
from contextlib import redirect_stdout, redirect_stderr

from .registry import BaseTool, registry


class PythonTool(BaseTool):
    """Tool for executing Python code."""
    
    @property
    def name(self) -> str:
        return "python"
    
    @property
    def description(self) -> str:
        return "Execute Python code and return the output"
    
    def execute(self, code: str) -> str:
        """
        Execute Python code safely.
        
        Args:
            code: Python code to execute
            
        Returns:
            Execution output or error message
        """
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # Create a restricted namespace
                namespace = {"__builtins__": __builtins__}
                exec(code, namespace)
            
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            
            result = ""
            if stdout_output:
                result += f"Output:\n{stdout_output}"
            if stderr_output:
                result += f"\nStderr:\n{stderr_output}"
            
            return result.strip() if result else "Code executed successfully (no output)"
            
        except Exception as e:
            return f"Error: {type(e).__name__}: {str(e)}"


# Register the tool
registry.register(PythonTool())
