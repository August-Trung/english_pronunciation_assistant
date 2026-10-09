import uvicorn
import os

try:
    import spaces
    @spaces.GPU(duration=1)
    def zero_gpu_dummy():
        return True
    try:
        zero_gpu_dummy()
    except Exception as gpu_err:
        print("ZeroGPU Execution Notice:", gpu_err)
except Exception as e:
    print("ZeroGPU Import Notice:", e)

from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
