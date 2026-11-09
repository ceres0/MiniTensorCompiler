# from tvm.script import ir as I
# from tvm.script import tirx as T
# from tvm.tirx.layout import Axis

@I.ir_module
class Module:
    @T.prim_func
    def main(A: T.Buffer((1, 128), "float32"), W: T.Buffer((128, 256), "float32"), B: T.Buffer((256,), "float32"), C: T.Buffer((1, 256), "float32")):
        T.func_attr({"tirx.noalias": True})
        for i, j in T.grid(1, 256):
            acc: T.float32 = T.float32(0.0)
            for r in range(128):
                acc = acc + A[i, r] * W[r, j]
            C[i, j] = T.max(acc + B[j], T.float32(0.0))
