# from tvm.script import ir as I
# from tvm.script import tirx as T
# from tvm.tirx.layout import Axis

@I.ir_module
class Module:
    @T.prim_func(s_tir=True)
    def main(A: T.Buffer((17, 65), "float32"), B: T.Buffer((65, 70), "float32"), C: T.Buffer((17, 70), "float32")):
        T.func_attr({"tirx.noalias": True})
        # with T.sblock("root"):
        for i in T.thread_binding(17, thread="blockIdx.y"):
            for j_0 in T.thread_binding(1, thread="blockIdx.x"):
                for j_1 in T.thread_binding(128, thread="threadIdx.x"):
                    for r in range(65):
                        with T.sblock("matmul"):
                            vi = T.axis.spatial(17, i)
                            vj = T.axis.spatial(70, j_0 * 128 + j_1)
                            vr = T.axis.reduce(65, r)
                            T.where(j_0 * 128 + j_1 < 70)
                            T.reads(A[vi, vr], B[vr, vj])
                            T.writes(C[vi, vj])
                            with T.init():
                                C[vi, vj] = T.float32(0.0)
                            C[vi, vj] = C[vi, vj] + A[vi, vr] * B[vr, vj]
