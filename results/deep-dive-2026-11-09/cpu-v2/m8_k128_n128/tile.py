# from tvm.script import ir as I
# from tvm.script import tirx as T
# from tvm.tirx.layout import Axis

@I.ir_module
class Module:
    @T.prim_func(s_tir=True)
    def main(A: T.Buffer((8, 128), "float32"), B: T.Buffer((128, 128), "float32"), C: T.Buffer((8, 128), "float32")):
        T.func_attr({"tirx.noalias": True})
        # with T.sblock("root"):
        for i_0, i_1, j_0, j_1, r_0, r_1 in T.grid(1, 8, 4, 32, 16, 8):
            with T.sblock("matmul"):
                vi = T.axis.spatial(8, i_0 * 8 + i_1)
                vj = T.axis.spatial(128, j_0 * 32 + j_1)
                vr = T.axis.reduce(128, r_0 * 8 + r_1)
                T.reads(A[vi, vr], B[vr, vj])
                T.writes(C[vi, vj])
                with T.init():
                    C[vi, vj] = T.float32(0.0)
                C[vi, vj] = C[vi, vj] + A[vi, vr] * B[vr, vj]
