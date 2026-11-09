# from tvm.script import ir as I
# from tvm.script import tirx as T
# from tvm.tirx.layout import Axis

@I.ir_module
class Module:
    @T.prim_func(s_tir=True)
    def main(A: T.Buffer((1, 256), "float32"), B: T.Buffer((256, 256), "float32"), C: T.Buffer((1, 256), "float32")):
        T.func_attr({"tirx.noalias": True})
        # with T.sblock("root"):
        for i, j, r in T.grid(1, 256, 256):
            with T.sblock("matmul"):
                vi, vj, vr = T.axis.remap("SSR", [i, j, r])
                T.reads(A[vi, vr], B[vr, vj])
                T.writes(C[vi, vj])
                with T.init():
                    C[vi, vj] = T.float32(0.0)
                C[vi, vj] = C[vi, vj] + A[vi, vr] * B[vr, vj]
