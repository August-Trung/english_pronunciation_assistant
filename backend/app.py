import uvicorn
from core.main import app

# ZeroGPU Supervisor compatibility fallback
try:
    import spaces
    @spaces.GPU
    def _zero_gpu_init():
        return True
    _zero_gpu_init()
except Exception as e:
    print("ZeroGPU init notice:", e)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
