# from tvm.script import ir as I
# from tvm.script import relax as R

@I.ir_module
class Module:
    @R.function
    def main(a: R.Tensor((17, 65), dtype="float32"), b: R.Tensor((65, 70), dtype="float32")) -> R.Tensor((17, 70), dtype="float32"):
        with R.dataflow():
            gv: R.Tensor((17, 70), dtype="float32") = R.matmul(a, b, out_dtype=None)
            R.output(gv)
        return gv
