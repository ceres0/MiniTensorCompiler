# CUDA toolkit for TVM GPU code generation; the host must provide NVIDIA drivers.
FROM nvidia/cuda:13.0.2-base-ubuntu24.04@sha256:2ab6381d970b211fb93853796dc6707eb8a72575a375c422b17cf4d8b2641701

COPY --from=ghcr.io/astral-sh/uv:0.11.6@sha256:b1e699368d24c57cda93c338a57a8c5a119009ba809305cc8e86986d4a006754 /uv /uvx /usr/local/bin/

ENV UV_PYTHON_INSTALL_DIR=/opt/uv/python \
    UV_PYTHON_PREFERENCE=only-managed \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/tmp/uv-cache \
    CUDA_HOME=/usr/local/cuda \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/workspace/.venv/bin:/usr/local/cuda/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential ca-certificates git libgomp1 \
    cuda-nvcc-13-0=13.0.88-1 cuda-cudart-dev-13-0=13.0.96-1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
ARG INCLUDE_MODELS=0
COPY pyproject.toml uv.lock ./
RUN case "$INCLUDE_MODELS" in \
    1) uv sync --locked --python 3.11.15 --extra dev --extra gpu --extra models --no-install-project ;; \
    0) uv sync --locked --python 3.11.15 --extra dev --extra gpu --no-install-project ;; \
    *) echo "INCLUDE_MODELS must be 0 or 1" >&2; exit 1 ;; esac
COPY . .
ENV PYTHONPATH=/workspace

# GPU access is opt-in at runtime via the NVIDIA Container Toolkit and --gpus.
# The existing project doctor reports the environment; it does not claim GPU execution.
CMD ["python", "-m", "minicompiler", "doctor"]
