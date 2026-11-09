# from tvm.script import ir as I
# from tvm.script import tirx as T
# from tvm.tirx.layout import Axis
# from tvm.script import relax as R

@I.ir_module
class Module:
    @T.prim_func(private=True, s_tir=True)
    def matmul(a: T.Buffer((T.int64(8), T.int64(256)), "float32"), b: T.Buffer((T.int64(256), T.int64(256)), "float32"), matmul: T.Buffer((T.int64(8), T.int64(256)), "float32")):
        T.func_attr({"tirx.noalias": True})
        # with T.sblock("root"):
        for i0, i1, k in T.grid(T.int64(8), T.int64(256), T.int64(256)):
            with T.sblock("matmul"):
                v_i0, v_i1, v_k = T.axis.remap("SSR", [i0, i1, k])
                T.reads(a[v_i0, v_k], b[v_k, v_i1])
                T.writes(matmul[v_i0, v_i1])
                with T.init():
                    matmul[v_i0, v_i1] = T.float32(0.0)
                matmul[v_i0, v_i1] = matmul[v_i0, v_i1] + a[v_i0, v_k] * b[v_k, v_i1]

    @R.function
    def main(a: R.Tensor((8, 256), dtype="float32"), b: R.Tensor((256, 256), dtype="float32")) -> R.Tensor((8, 256), dtype="float32"):
        cls = Module
        with R.dataflow():
            gv = R.call_tir(cls.matmul, (a, b), out_ty=R.Tensor((8, 256), dtype="float32"))
            R.output(gv)
        return gv
