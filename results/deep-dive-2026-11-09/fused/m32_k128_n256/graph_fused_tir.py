# from tvm.script import ir as I
# from tvm.script import tirx as T
# from tvm.tirx.layout import Axis
# from tvm.script import relax as R

@I.ir_module
class Module:
    @T.prim_func(private=True, s_tir=True)
    def fused_relax_matmul_relax_add_relax_nn_relu(x: T.Buffer((T.int64(32), T.int64(128)), "float32"), w: T.Buffer((T.int64(128), T.int64(256)), "float32"), bias: T.Buffer((T.int64(256),), "float32"), compute_intermediate: T.Buffer((T.int64(32), T.int64(256)), "float32")):
        T.func_attr({"tirx.noalias": True})
        # with T.sblock("root"):
        matmul_intermediate = T.sblock_alloc_buffer((T.int64(32), T.int64(256)))
        T_add_intermediate = T.sblock_alloc_buffer((T.int64(32), T.int64(256)))
        for i0, i1, k in T.grid(T.int64(32), T.int64(256), T.int64(128)):
            with T.sblock("matmul"):
                v_i0, v_i1, v_k = T.axis.remap("SSR", [i0, i1, k])
                T.reads(x[v_i0, v_k], w[v_k, v_i1])
                T.writes(matmul_intermediate[v_i0, v_i1])
                with T.init():
                    matmul_intermediate[v_i0, v_i1] = T.float32(0.0)
                matmul_intermediate[v_i0, v_i1] = matmul_intermediate[v_i0, v_i1] + x[v_i0, v_k] * w[v_k, v_i1]
        for ax0, ax1 in T.grid(T.int64(32), T.int64(256)):
            with T.sblock("T_add"):
                v_ax0, v_ax1 = T.axis.remap("SS", [ax0, ax1])
                T.reads(matmul_intermediate[v_ax0, v_ax1], bias[v_ax1])
                T.writes(T_add_intermediate[v_ax0, v_ax1])
                T_add_intermediate[v_ax0, v_ax1] = matmul_intermediate[v_ax0, v_ax1] + bias[v_ax1]
        for i0, i1 in T.grid(T.int64(32), T.int64(256)):
            with T.sblock("compute"):
                v_i0, v_i1 = T.axis.remap("SS", [i0, i1])
                T.reads(T_add_intermediate[v_i0, v_i1])
                T.writes(compute_intermediate[v_i0, v_i1])
                compute_intermediate[v_i0, v_i1] = T.max(T_add_intermediate[v_i0, v_i1], T.float32(0.0))

    @R.function
    def main(x: R.Tensor((32, 128), dtype="float32"), w: R.Tensor((128, 256), dtype="float32"), bias: R.Tensor((256,), dtype="float32")) -> R.Tensor((32, 256), dtype="float32"):
        cls = Module
        with R.dataflow():
            gv = R.call_tir(cls.fused_relax_matmul_relax_add_relax_nn_relu, (x, w, bias), out_ty=R.Tensor((32, 256), dtype="float32"))
            R.output(gv)
        return gv
