import subprocess
import sys

def run_diagnostic():
    """Run diagnostic and return output"""
    try:
        result = subprocess.run(
            [sys.executable, "quick_diagnostic.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print("=== DIAGNOSTIC OUTPUT ===")
        print(result.stdout)
        
        if result.stderr:
            print("=== ERRORS ===")
            print(result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("Diagnostic timed out")
        return False
    except Exception as e:
        print(f"Error running diagnostic: {e}")
        return False

if __name__ == "__main__":
    success = run_diagnostic()
    print(f"\nDiagnostic {'PASSED' if success else 'FAILED'}")