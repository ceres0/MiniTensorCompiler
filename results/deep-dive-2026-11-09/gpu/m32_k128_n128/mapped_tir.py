# from tvm.script import ir as I
# from tvm.script import tirx as T
# from tvm.tirx.layout import Axis

@I.ir_module
class Module:
    @T.prim_func(s_tir=True)
    def main(A: T.Buffer((32, 128), "float32"), B: T.Buffer((128, 128), "float32"), C: T.Buffer((32, 128), "float32")):
        T.func_attr({"tirx.noalias": True})
        # with T.sblock("root"):
        for i in T.thread_binding(32, thread="blockIdx.y"):
            for j_0 in T.thread_binding(1, thread="blockIdx.x"):
                for j_1 in T.thread_binding(128, thread="threadIdx.x"):
                    for r in range(128):
                        with T.sblock("matmul"):
                            vi = T.axis.spatial(32, i)
                            vj = T.axis.spatial(128, j_0 * 128 + j_1)
                            vr = T.axis.reduce(128, r)
                            T.reads(A[vi, vr], B[vr, vj])
                            T.writes(C[vi, vj])
                            with T.init():
                                C[vi, vj] = T.float32(0.0)
                            C[vi, vj] = C[vi, vj] + A[vi, vr] * B[vr, vj]
