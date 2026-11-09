# from tvm.script import ir as I
# from tvm.script import relax as R

@I.ir_module
class Module:
    @R.function
    def main(a: R.Tensor((1, 128), dtype="float32"), b: R.Tensor((128, 128), dtype="float32")) -> R.Tensor((1, 128), dtype="float32"):
        with R.dataflow():
            gv: R.Tensor((1, 128), dtype="float32") = R.matmul(a, b, out_dtype=None)
            R.output(gv)
        return gv
